services:
  - type: web
    name: besight-bot
    env: python
    startCommand: ./start.sh
    buildCommand: pip install -r requirements.txt
