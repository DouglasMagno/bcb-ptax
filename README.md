# BCB PTAX

### Online
[![deployed](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](http://bcb-ptax.herokuapp.com/swagger/)

Web scraping bot that seeks data from the central bank of Brazil on dollar and euro quotations.

# Requirements

  - Docker

### Installation

```sh
docker run -d --name bcb-ptax -p 5000:5000 dougmagno/bcbptax:latest
```

### Open Swagger
```
http://localhost:5000/swagger
```
And see the availables endpoints
