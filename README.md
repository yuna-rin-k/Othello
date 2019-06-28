# Homework 6

1. Use github fork to make your own repository for your changes.
2. Use `git clone` to clone your repository to your local computer.
3. Create a new Google Cloud project using `gcloud projects create --set-as-default your-awesome-bot-name`.
5. `gcloud app deploy python/` or `gcloud app deploy go/` to deploy your app.
6. Add the appspot address to the ["Reversi Players" sheet](https://docs.google.com/spreadsheets/d/1UaFboojs_saqX-B4f1rAXhun74eTMdAQToo6_mGKQPs/edit)
7. **Modify the source code to change the way a move is picked**
8. Re-deploy the app
9. Repeat steps 7 and 8 until you have a very clever AI :)
10. eventually push your awesome clever AI to github.
    * If you want to keep it secret until Thursday night, that's fine.
    * Sharing and talking about your ideas is a good way to improve your designs, so you're encouraged to share!
11. Email step2019-homework and your mentor with your github repository link.

# Using reflector.go

You can use this ["reflector"
program](https://github.com/step2019/hw6/blob/master/reflector.go) to make a
locally running dev_appserver instance act like a human player. This way you
don't have to deploy the whole app to have it run a whole game between AIs.

To use it:
* [Download](https://golang.org/dl/) and install Go if you don't have it already.
* Start your bot with `dev_appserver.py go` or`dev_appserver.py python`.
* Start a new game on https://step-reversi.appspot.com with a "Human (or Local
  bot)" selected as one of the players
* Copy the command displayed at the bottom of the game viewer page like `go run
  reflector.go "https://step-reversi.appspot.com/view?gamekey=fOoBaR"` and paste
  it into a teminal window in your `hw6` directory.
    * (but pasting your actual viewer URL there -- fOoBaR is not a real game ;)
* Your bot will play as the human(s) in that game.

