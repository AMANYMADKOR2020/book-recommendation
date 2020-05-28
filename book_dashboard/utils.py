import pandas as pd
import os
from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
import joblib
from sklearn.pipeline import Pipeline



## create the dataset paths and pickles path
PICKLES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pickles")
item_info_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"items_info.dat")
book_rating_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'book_ratings.dat')
# if the folder doesn't exist
if not os.path.exists(PICKLES_PATH):
    os.mkdir(PICKLES_PATH)
##start reading the datasets
item_info_ds = pd.read_csv(item_info_path, sep='\t',error_bad_lines=False,index_col=False)
book_rating_ds = pd.read_csv(book_rating_path,sep='\t')
## rename the column Book_ID  to git rid of space
item_info_ds.rename(columns={'Book_ID ':'Book_ID' }, inplace=True)
## add new column avg_rating to show the mean of all ratings on this book
item_info_ds['rating']=item_info_ds['Book_ID'].apply(lambda x:book_rating_ds.loc[book_rating_ds['item']==x,"rating"].mean())
output_dataset=item_info_ds.sort_values(by='rating',ascending=False)[:5]
output_dataset=output_dataset[['Book-Title','Book-Author','Publisher','Year-Of-Publication','Image-URL-L','rating']]

def train():
     reader = Reader(rating_scale=(1,10))
     data=Dataset.load_from_df(book_rating_ds[['user','item','rating']],reader)
     sim_options={    "name":"cosine",    "user_based":False}
     model=KNNWithMeans(sim_options=sim_options)
     training_Set=data.build_full_trainset()
     model.fit(training_Set)
    # export the model
     model_path = os.path.join(PICKLES_PATH, "rec.pkl")
     joblib.dump(model, model_path, compress=True)

def load_model():
    model_path = os.path.join(PICKLES_PATH, "rec.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        train()
        return joblib.load(model_path)



def top_5_recommendations(uid):
    model = load_model()
    books_rated_by_user=book_rating_ds.loc[book_rating_ds['user']==uid,"item"].values
    other_books=item_info_ds.loc[~item_info_ds['Book_ID'].isin(books_rated_by_user)]
    if uid not in set (book_rating_ds['user']):
        print("is not a user")
        output_dataset=other_books.sort_values(by='rating',ascending=False)[:5]
        output_dataset=output_dataset[['Book-Title','Book-Author','Publisher','Year-Of-Publication','Image-URL-L','rating']]
        return output_dataset
    other_books['rating']=item_info_ds['Book_ID'].apply(lambda x :model.predict(uid,x).est)
    print("is a user")
    output_dataset=other_books.sort_values(by='rating',ascending=False)[:5]
    output_dataset=output_dataset[['Book-Title','Book-Author','Publisher','Year-Of-Publication','Image-URL-L','rating']]
    return output_dataset

def get_output_dataset():
    return output_dataset

if __name__ == "__main__":
    train()
    model = load_model()
    ds=top_5_recommendations(200)
    print(ds)