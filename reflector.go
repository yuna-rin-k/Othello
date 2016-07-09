// Reflector attaches a locally running Othello bot to the remote
// Othello match server.
package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
)

var (
	gameKey  = flag.String("gamekey", "", "gamekey of game to get state from and send moves to")
	whiteKey = flag.String("whitekey", "", "player key for white. required to reflect moves as white")
	blackKey = flag.String("blackkey", "", "player key for black. required to reflect moves as white")

	bot = flag.String("bot", "http://localhost:8080", "what service to reflect for getting moves")
)

const (
	kServer = "https://3-dot-step-othello.appspot.com"
)

var baseURL url.URL

func init() {
	parsed, err := url.Parse(kServer)
	if err != nil {
		panic(err)
	}
	baseURL = *parsed
}

func exitUsage() {
	fmt.Print(`usage: reflector [flags] [game viewer URL]
Examples:
  reflector --gamekey=foo --whitekey=bar
  reflector "http://step-othello.appspot.com/view?gamekey=foo&whitekey=bar"
  reflector --whitekey=bar http://step-othello.appspot.com/view?gamekey=foo

All of the above will start playing game "foo" as white using the
player key "bar". The quotes around the full URL in the second case are
usually necessary to avoid having the shell interpret the & as a special
shell control character.
`)
	flag.PrintDefaults()
	os.Exit(1)
}

// parseURL parses the given viewURL to set flags.
func parseURL(view string) error {
	u, err := url.Parse(view)
	if err != nil {
		return err
	}
	vals, err := url.ParseQuery(u.RawQuery)
	if err != nil {
		return fmt.Errorf("bad query params in %v: %v", view, err)
	}
	for k, v := range vals {
		flag.Set(k, v[0])
	}
	return nil
}

// setParams sets the basic URL game parameters on u from flags.
func setParams(u *url.URL, extra url.Values) {
	vals := make(url.Values)
	vals.Set("gamekey", *gameKey)
	if len(*whiteKey) > 0 {
		vals.Set("whitekey", *whiteKey)
	}
	if len(*blackKey) > 0 {
		vals.Set("blackkey", *blackKey)
	}
	if extra != nil {
		for k, v := range extra {
			vals[k] = v
		}
	}
	u.RawQuery = vals.Encode()
}

// newURL makes a new URL pointing the given path from the current
// baseURL, including the basic params and the the given extra values.
func newURL(path string, extra url.Values) url.URL {
	u := baseURL
	u.Path = path
	setParams(&u, extra)
	return u
}

type Piece int8

const (
	Empty Piece = iota
	Black Piece = iota
	White Piece = iota
	Tie   Piece = iota
)

func (p Piece) String() string {
	switch p {
	case White:
		return "White/O/Blue"
	case Black:
		return "Black/X/Red"
	case Tie:
		return "neither"
	}
	panic(fmt.Errorf("invalid piece: %#v", p))
}

type game struct {
	// A winner signals that the game is over and we should shut down.
	Winner Piece `json:winner`
}

// getGame gets the raw JSON for a game and also the winner if there
// is one.
func getGame(viewer url.URL) (string, Piece, error) {
	var g game
	log.Printf("reading game state from %v", viewer.String())
	resp, err := http.Get(viewer.String())
	if err != nil {
		return "", g.Winner, err
	}
	defer resp.Body.Close()
	var buf bytes.Buffer
	dec := json.NewDecoder(io.TeeReader(resp.Body, &buf))
	err = dec.Decode(&g)
	if err != nil {
		return buf.String(), g.Winner, fmt.Errorf("failed to parse json (%q): %v", buf.String(), err)
	}
	return buf.String(), g.Winner, nil
}

func main() {
	flag.Parse()
	if len(flag.Args()) > 0 {
		if err := parseURL(flag.Arg(0)); err != nil {
			log.Print(err)
			exitUsage()
		}
	}
	if len(*gameKey) < 1 && (len(*whiteKey) < 1 || len(*blackKey) < 1) {
		fmt.Println("Need a gamekey and at least one player key")
		exitUsage()
	}

	viewer := newURL("/get", nil)
	for {
		game, winner, err := getGame(viewer)
		if err != nil {
			log.Fatalf("failed to get game: %v", err)
		}
		if winner != Empty {
			fmt.Printf("game is over: %v won!", winner)
		}
		fmt.Println(game)
		os.Exit(0)
	}
}
