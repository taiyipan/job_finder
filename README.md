# Job Finder AI
## powered by: data mining, web automation, deep learning, TensorFlow, Google's Universal Sentence Encoder
Do you find job hunting in this modern world such boring work, just as I do?
Fear not, here is an AI job finder software for you!
The AI learns from your job preferences and automatically browse Indeed everyday
and send you personalized new job recommendations tailored to you.
Say goodbye to hours of your life wasted on chores,
and spend the minimal time to send over resumes.
Focus on what's important in life. Automate away the chores.

In development, this project is divided into 3 parts.
1. Data mining and labeling
2. Train, evaluate, and export deep learning model
3. Indeed crawler

In production, the task is shared between 2 computers or virtual machines.
1. Computer A performs daily web crawling on Indeed.com and collects new jobs in the area.
2. Computer B acts as the TensorFlow model server.
3. A collects input data, sends to B.
4. B performs 1 batched feedforward pass on its neural net, and sends output vector to A.
5. A interprets the output vector, and compiles report of its findings, sends to human user.

![alt text](img/output_sample.jpg)
![alt text](img/p0.9.png)
![alt text](img/p0.5.png)
![alt text](img/neural_net_architecture.PNG)
