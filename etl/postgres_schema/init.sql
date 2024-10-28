CREATE TABLE Participants (
    participant_id SERIAL PRIMARY KEY,
    gender VARCHAR(10),
    age INT
    
);

CREATE TABLE Eeg_data_train (
    eeg_train_id SERIAL PRIMARY KEY,
    participant_id INT,
    channel_name VARCHAR,
    channel_mean FLOAT,
    sleep_status VARCHAR(10) CHECK (sleep_status IN ('good sleep', 'bad sleep')),
    CONSTRAINT fk_Eeg_data_Participants FOREIGN KEY (participant_id) REFERENCES Participants (participant_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Eeg_data_test (
    eeg_test_id SERIAL PRIMARY KEY,
    participant_id INT,
    channel_name VARCHAR,
    channel_mean FLOAT,
    sleep_status VARCHAR(10) CHECK (sleep_status IN ('good sleep', 'bad sleep')),
    CONSTRAINT fk_Eeg_data_Participants FOREIGN KEY (participant_id) REFERENCES Participants (participant_id) ON DELETE RESTRICT ON UPDATE CASCADE
);