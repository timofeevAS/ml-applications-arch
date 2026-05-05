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