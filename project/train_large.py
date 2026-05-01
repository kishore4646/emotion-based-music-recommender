import src.model as m

# Use the large dataset if present
m.DATASET_PATH = m.DATASET_PATH.replace('dataset.csv','dataset_108k.csv')
print('Using dataset:', m.DATASET_PATH)

m.train_model(save=True)
