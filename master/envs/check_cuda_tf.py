import tensorflow as tf

print("tensorflow version:", tf.__version__)
print("cuda available:", tf.test.is_gpu_available())