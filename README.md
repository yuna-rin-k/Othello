# Homework 7

1. Fork a copy for your changes
2. Clone it to your local workstation
3. Create a new project to host your AI in https://console.cloud.google.com
4. Update the "application" field in app.yaml to match your application id
5. `appcfg.py update python/` or `goapp deploy go/` to deploy your app
6. Add the appspot address to the ["Othello Players" sheet](https://docs.google.com/spreadsheets/d/1j2M92fZQjblAj3KPaLI2NJ0mkFS4dLv85jizmoMn3m0/edit#gid=0)
7. **Modify the way a move is picked**
8. re-deploy the app
9. repeat steps 7 and 8 until you have a very clever AI :)
10. eventually push your awesome clever AI to github.
    * If you want to keep it secret until Thursday night, that's fine.
11. email step16 with your github repository link as usual.

# Using reflector.go

You can use this "reflector" program to make a locally running dev_appserver instance act like a human player (i.e. you don't have to deploy the whole app to have it run a game).

To run it:
* [download](https://golang.org/dl/) and install Go if you don't have it already.
* Start a new game on https://step-othello.appspot.com with a "Human (or Local bot)" selected as one of the players
* copy the URL of that browser tab showing that game (i.e. a URL that looks like "https://step-othello.appspot.com/view?gamekey=fOoBaR")
* type `go run reflector.go "https://step-othello.appspot.com/view?gamekey=fOoBaR"`
    * (but pasting your actual viewer URL there -- fOoBaR is not a real game ;)
