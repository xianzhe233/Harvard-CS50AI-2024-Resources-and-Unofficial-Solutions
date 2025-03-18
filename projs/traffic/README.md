# Experimentation Process


## 1st

### Structure
- convolutional layer: 32 (3, 3) relu
- pooling layer: max-pooling (2, 2) 
- hidden layer: 128 relu

### Result
- accuracy: 0.9371
- loss: 0.4126


## 2nd

### Structure
- convolutional layer: 32 (3, 3) relu
- pooling layer: max-pooling (2, 2) 
- hidden layer:
  - 128 relu
  - 64 relu
  - dropout 0.1

### Result
- accuracy: 0.9177
- loss: 0.3708


## 3rd

### Structure
- convolutional layer: 32 (3, 3) relu
- pooling layer: max-pooling (2, 2) 
- hidden layer:
  - 256 relu
  - 128 relu
  - 128 relu

### Result
- accuracy: 0.9522
- loss: 0.2432