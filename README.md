# Brief Introduction

A program to conduct sentiment analysis on media reports about Chinese listed companies.

# File Structure   

    .
    ├── README.md
    ├── corpus
    │   ├── pos_data.txt    Positive Corpus
    │   ├── neg_data.txt    Negative Corpus
    │   ├── pos_dict.txt    Positive Dictionary
    │   └── neg_dict.txt    Negative Dictionary
    ├── model
    │   └── train_model.pkl    Model Generated After Training
    └── src
        ├── rawData.py    Fetch Data & Segment Article
        ├── svm.py    Feature Extraction & Training
        ├── dict.py    Prediction Based on Dictionary
        ├── main.py    Calculate Each Article's Sentiment Value
        ├── midas_util.py     Tool Functions
        └── media_cluster.py    Clustering

# Run    
    · Run main.py to calculate each article's sentiment value     
    · Run media_cluster.py to cluster all companies       

# Result Explanation   
    · Each article will be finally judged as Positive, Neutral or Negative   
    · Blank articles are judges as 'Neutral'      
    · In cluster.csv, the num_cluster is set as 10, which corresponds to 10 media evaluation levels
