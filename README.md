# Social Media API

The RESTful API is designed to manage post-related information and operations. This service provides a convenient way to interact with different resources such as profiles, hashtags, and posts.

## Run with Docker

**Docker must already be installed!**

```shell
git clone https://github.com/vitalii-babiienko/social-media-api.git
cd social-media-api
```

Create a **.env** file by copying the **.env.sample** file and populate it with the required values.

```shell
docker-compose up --build
```

## Get access

* Create a new user via [api/user/register/](http://localhost:8000/api/user/register/).
* Take the access and refresh tokens via [api/user/token/](http://localhost:8000/api/user/token/).
* Refresh the access token via [api/user/token/refresh/](http://localhost:8000/api/user/token/refresh/).

## API Documentation

The API is well-documented with detailed explanations of each endpoint and its functionalities. The documentation provides sample requests and responses to help you understand how to interact with the API. The documentation is available via [api/doc/swagger/](http://localhost:8000/api/doc/swagger/).
