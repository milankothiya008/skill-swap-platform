# Skill Swap Platform

A Flask-based web application that connects people who want to exchange skills with each other.

![Skill Swap Screenshot](static/screenshot.png) <!-- Add a screenshot later -->

## Features

- *User Profiles*:
  - Create and manage your profile
  - List skills you can offer and skills you want to learn
  - Upload profile pictures (using Cloudinary)

- *Skill Matching*:
  - Search for users by skills
  - Browse available skill exchanges
  - Request skill swaps from other users

- *Request Management*:
  - Send and receive skill swap requests
  - Accept or reject incoming requests
  - Email notifications for requests and responses

- *User Rating System*:
  - Rate your skill swap experiences
  - View other users' ratings

## Technologies Used

- *Backend*:
  - Python 3
  - Flask
  - Flask-SQLAlchemy
  - PostgreSQL (hosted on Railway)
  - Cloudinary (for image storage)

- *Frontend*:
  - HTML5
  - CSS3
  - JavaScript (basic interactivity)
  - Font Awesome (icons)

- *Services*:
  - Flask-Mail (for email notifications)
  - Cloudinary (image upload and storage)
  - Railway (database hosting)

## Installation

1. *Clone the repository*:
   ```bash
   git clone https://github.com/yourusername/skill-swap.git
   cd skill-swap