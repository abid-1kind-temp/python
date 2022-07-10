from typing import Text
from pyparsing import Word
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import numpy as np
from textblob import TextBlob
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)

# Create an engine instance
alchemyEngine = create_engine('postgresql+psycopg2://<db_username>:<password>@<hostname>:<port>/<db_name>', pool_recycle=3600)

# Connect to PostgreSQL server
dbConnection = alchemyEngine.connect()

# Read data from PostgreSQL database table and load into a DataFrame instance
df = pd.read_sql("select * from \"google_news\"", dbConnection)
pd.set_option('display.expand_frame_repr', False)

# Close the database connection
dbConnection.close()

# Set date as index
df = df.set_index(pd.DatetimeIndex(df['published_date'].values))

# Omit any duplicate or null records
df.drop_duplicates(inplace = True)
df.dropna(axis = 0, inplace = True)

# Analyse sentiment
def sentimentAnalysis():
    # Get polarity
    def getPolarity(text):
        return TextBlob(text).sentiment.polarity

    # Create polarity column
    df['Polarity'] = df['title'].apply(getPolarity)

    # Compute sentiment
    def getSentiment(score):
        if score < 0:
            return 'Negative'
        elif score == 0:
            return 'Neutral'
        else:
            return 'Positive'

    # Create sentiment column
    df['Sentiment'] = df['Polarity'].apply(getSentiment)

    # Polarity based on dates
    polarity = df.groupby(['published_date']).sum()['Polarity']

    # Average sentiment
    polarity_count = df.groupby(['published_date']).count()['Polarity']
    polarity_avg = polarity / polarity_count

    # Draw graphs for news sentiment
    fig = plt.figure()

    ax1 = fig.add_subplot(211)
    ax1.plot(polarity.index, polarity)
    ax1.set_title("Global Economy Sentiment Over Last Week")

    ax2 = fig.add_subplot(212)
    ax2.plot(polarity_avg.index, polarity_avg)
    ax2.set_title("Average Economic Sentiment Over Last Week")

    fig.set_size_inches(10, 5)
    fig.tight_layout()
    fig.text(0.5, 0.01, 'DATE', ha='center', va='center')
    fig.text(0.01, 0.5, 'SENTIMENT', ha='center', va='center', rotation='vertical')

    plt.show()

sentimentAnalysis()