import psycopg2
import pandas as pd
import time
import mne
import os
import fnmatch
import asyncio


current_path = os.getcwd()
print("Current Path:", current_path)


def find_specific_files(directory, pattern):
    matched_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if fnmatch.fnmatch(file, pattern):
                matched_files.append(os.path.join(root, file))
    return matched_files


def insert_participants():
    file_path = '/dataset/participants.tsv'
    participants_data = pd.read_csv(file_path, sep='\t')

    for index, row in participants_data.iterrows():
        if row['SessionOrder'].startswith("NS"):

            cursor.execute("""
                INSERT INTO Participants (gender, age)
                VALUES (%s, %s)
                """,
                (row['Gender'], row['Age'])
            )

    connection.commit()
    print("insert participants success")

async def load_eeg_data(real_index, i):

    try:
        raw_data = mne.io.read_raw_eeglab(f'/dataset/sub-{real_index+1:02}/ses-{i+1}/eeg/sub-{real_index+1:02}_ses-{i+1}_task-eyesclosed_eeg.set')

        reduce_data = 1
        while reduce_data > 0:
            try:
                # แบ่งเอามาแค่ 1 - reduce_data % พอ
                eeg_data = raw_data.get_data(start=0, stop=int(raw_data.n_times * reduce_data))
                channel_means = eeg_data.mean(axis=1)
                reduce_data = 1

                # reduce จะทำให้ทุกๆ data มีความยาวมากสุดเท่าที่เป็นไปได้ เพื่อนำไปหาค่าเฉลี่ย
                break
            except Exception as e:
                print(f"data ยังเสียหายในช่วง {reduce_data} กำลัง reduce เพื่อแก้ไข")
                reduce_data -= 0.05
        
        return raw_data, channel_means
    except Exception as e:
        print(f"เกิดข้อผิดพลาดที่ sub-{real_index+1}: {e}")
        return None, None

async def insert_eeg_data(i, files, sleep_status):

    #มีไฟล์ หลับตาแค่ 38 ที่เหลือมีแต่ลืมตา
    print("สรุป files ก่อนจะลด label ตรงนอนไม่พอออก มี:", len(files))


    # ตรวจสอบลำดับ
    label = '/dataset/participants.tsv'
    checking_label = pd.read_csv(label, sep='\t')

    for index, row in checking_label.iterrows():
        if not str(row['SessionOrder']).startswith("NS"):
            checking_label.drop(index=index,inplace=True)

    # เอาเฉพาะ คนที่เริ่มจาก นอนพอ จากนั้น นอนไม่พอ
    files = [path for path in files if checking_label['participant_id'].isin([path.split('/')[2]]).any()]


    print("สรุป files หลังลด label ตรงนอนไม่พอออก มี:", len(files))

    
    for j in range(len(files)):
    # for j, _ in checking_label.iterrows():

        split_result = files[j].split('-')[1].split('/')[0]

        # เอา index จริงที่ข้ามได้ และอยู่ภายใน 38 คนแรกที่มีไฟล์หลับตา
        real_index = int(split_result) - 1 # ลบ index เขย่ง ออก
        print(f"ค่า Real index คือ {real_index} และ {files[j]} ")

        raw_data, channel_means = await load_eeg_data(real_index, i)

        print("สรุป channel_means มี:", len(channel_means))
        print("สรุป enumerate มี:", len(tuple(enumerate(channel_means))))
        print("สรุป info มี:", len(raw_data.info['ch_names']))

        for idx, mean in enumerate(channel_means):
            cursor.execute("""
                            INSERT INTO Eeg_data (participant_id, channel_name, channel_mean, sleep_status)
                            VALUES (%s, %s, %s, %s)
                            """, (real_index+1, raw_data.info['ch_names'][idx], float(mean), sleep_status))
    connection.commit()
    print("insert eeg_data success")

# รอ PostgreSQL
time.sleep(3.5)

connection = psycopg2.connect(
    dbname='eeg_database',
    user='admin',
    password='css222',
    # อยู่ใน docker ต้องใช้ชื่อนี้
    host='etl-db-1',
    port='5432'
)
cursor = connection.cursor()



insert_participants()


for i in range(2):
    directory_path = "/dataset"

    file_pattern = "sub-*_ses-{}_*eyesclosed_eeg.set".format(i+1)

    files = find_specific_files(directory_path, file_pattern)


    sleep_status = ["good sleep", "bad sleep"]

    asyncio.run(insert_eeg_data(i, files, sleep_status=sleep_status[i]))


cursor.close()
connection.close()

print("Insert data success!!!!")