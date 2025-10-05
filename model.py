import tensorflow as tf
from tensorflow.keras import layers, models
import os

def build_model(timesteps, features):
    inp = layers.Input(shape=(timesteps, features))
    x = layers.Conv1D(32, 3, activation='relu', padding='same')(inp)
    x = layers.MaxPool1D(2)(x)
    x = layers.Conv1D(64, 3, activation='relu', padding='same')(x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(64, activation='relu')(x)
    out = layers.Dense(1, activation='sigmoid')(x)
    model = models.Model(inp, out)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def load_or_train_model(X=None, y=None, epochs=10, model_path=None):
    if model_path and os.path.exists(model_path):
        return tf.keras.models.load_model(model_path)
    assert X is not None and y is not None
    timesteps = X.shape[1]
    features = X.shape[2]
    model = build_model(timesteps, features)
    model.fit(X, y, epochs=epochs, batch_size=16)
    return model

def predict_changes(X, model_path='model_saved.h5'):
    model = tf.keras.models.load_model(model_path)
    preds = model.predict(X)
    return (preds > 0.5).astype(int).flatten()
