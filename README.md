# sketbot

# Description

This bot is for saving pictures sent in your discord server.
The bot is able to listen to specific chanels. 
It will safe these pictures locally and will create a reference to the path in a sql database.

# Future thoughts

The bot isnt finished by far. 
The ideas for the future is to train a neural network to identifie pictures with explicit content. 
This will give users the possibility to decide, whether they want explicit content stored on their server or not.
I will also add the functionality to delete these kind of pictures and warn users not to post these kind of things anymore.

# Functionality

The bot itself is running on an extern server, communicating with the discord API like it is used to be.
On the server there will be an SQL Database with all the infromation about the server, the picture got posted on and the user who posted it. 
The pictures will then be safed in the database.
Before a picture will be safed, a NN will mark the picture as NSFW or not.
