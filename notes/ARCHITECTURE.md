# Overview

End-to-end simple time series' missing data recovery system, which work in several scenarios:
 - batch recovery;
 - stream data recovery in soft real-time;
 - ML models registry retrain mechanism;
 - Connect new sensor;

 # System architecture
```mermaid
flowchart TD
    subgraph INPUTS["Input Sources"]
        SENSORS["External Sensor Sources"]
        SC["Sensor Configuration"]
    end

    subgraph ING["Ingestion Layer"]
        COLLECTOR["Collector / Ingestion Service"]
    end

    subgraph STREAM["Stream Layer"]
        MQ[["Kafka"]]
        CONS["Stream consumer"]
    end

    subgraph APP["Application Layer"]
        API["API / Web Application"]
    end

    subgraph RECOVERY["Recovery Processing Layer"]
        RJM["Recovery Job Manager"]
        RJM_MQ[["Kafka"]]
        RW["Recovery Workers"]
        INF["ML Inference Service"]
    end

    subgraph STORAGE["Storage Layer"]
        DB[("Application DB")]
        TSDB[("Time-Series DB")]
    end

    subgraph MLLIFE["ML Lifecycle Layer"]
        TRAIN["ML Model Manager / Training Service"]
        EVAL["Model Evaluation"]
        MR[("Model Registry")]
    end

    APP -. "create batch recovery job" .-> RECOVERY
    APP -. "start retraining" .-> TRAIN
    APP -. "configure sensors" .-> SC

    SENSORS --> COLLECTOR
    SC -.-> COLLECTOR

    COLLECTOR --> MQ

    MQ --> CONS 
    CONS --> RECOVERY


    RJM --job--> RJM_MQ
    RW -- take --> RJM_MQ
    RW --execute--> INF
    RECOVERY --> STORAGE

    STORAGE <--> APP
    STORAGE --> TRAIN

    TRAIN --> EVAL
    EVAL --> MR
    MR ==> INF

```

# Scenarios

## Scenario 1. Batch recovery of history data

1. User upload batch with data.
2. Prepare data.
3. Recognize missing values.
4. Process of recovering missing sensor's values.
5. Store resuilt into storage.
6. User get data with recovery missing values.

```mermaid
sequenceDiagram
    participant User
    participant App as API / Web Application
    participant Recovery as Recovery Processing Layer
    participant ML as ML Inference Service
    participant Storage as Storage Layer

    User->>App: Upload batch with data
    App->>Recovery: Batch
    Recovery->>Recovery: Recognize missing values
    Recovery->>ML: Recover missing sensor values
    ML-->>Recovery: Recovered values
    Recovery->>Storage: Store recovered data
    Storage-->>App: Recovered data
    App-->>User: Recovered data
```


## Scenario 2. Stream recovery data

1. Sensor sends new values.
2. Collect new data.
3. Prepare data.
4. Process of recovering missing sensor's values.
5. Store resuilt into storage.
6. User get data with recovery missing values.

```mermaid
sequenceDiagram
    participant Sensor
    participant Ingestion as Ingestion Layer
    participant Stream as Stream Layer
    participant Recovery as Recovery Processing Layer
    participant ML as ML Inference Service
    participant Storage as Storage Layer
    participant User
    participant App as API / Web Application

    Sensor->>Ingestion: Send new values
    Ingestion->>Ingestion: Collect new data
    Ingestion->>Stream: Prepare and publish data
    Stream->>Recovery: Consume prepared data
    Recovery->>ML: Recover missing sensor values
    ML-->>Recovery: Recovered values
    Recovery->>Storage: Store recovered data
    User->>App: Request data
    App->>Storage: Read data
    App-->>User: Return data
```

## Scenario 3. Add new sensor

1. User configure new sensor.
2. New sensor starts upload new data into system.
3. User get new label for view recognized data.

```mermaid
sequenceDiagram
    participant Admin as User
    participant App as API / Web Application
    participant Storage as Storage Layer
    participant Ingestion as Ingestion Layer
    participant Sensor as New Sensor

    Admin->>App: Configure new sensor
    App->>Storage: Save sensor configuration
    App->>Ingestion: Apply sensor configuration
    Sensor->>Ingestion: Upload new data
    Ingestion->>Storage: Store recognized sensor data
    Admin->>App: Open recognized data view
    App->>Storage: Read sensor labels and data
    App-->>Admin: Show new label
```

## Scenario 4. Repeat model learning process

1. There is new data in storage.
2. Administator start model learning process
3. New model version saved into registry.

```mermaid
sequenceDiagram
    participant Storage as Storage Layer
    participant Admin as User
    participant App as API / Web Application
    participant Training as ML Model Manager / Training Service
    participant Evaluation as Model Evaluation
    participant Registry as Model Registry
    participant Inference as ML Inference Service

    Storage->>Storage: New data is collected
    Admin->>App: Start model learning process
    App->>Training: Create retraining request
    Training->>Storage: Load training data
    Training->>Evaluation: Validate new model version
    Evaluation->>Registry: Save approved model version
    Registry-->>Inference: Provide latest model version
```
