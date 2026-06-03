# Exam Countdown

A simple countdown timer for an exam scheduled on **15 July 2026 at 10:30 AM IST**.

## Open Locally

Open `outputs/exam-countdown.html` in your browser.

## Open In VS Code

1. Open this folder in VS Code.
2. Open `outputs/exam-countdown.html`.
3. Right-click the file and choose **Open with Live Server** if you have the Live Server extension, or open the file directly in your browser.

## Publish With GitHub Pages

1. Create a new GitHub repository.
2. Push this folder to that repository.
3. In GitHub, go to **Settings > Pages**.
4. Set the source to the `main` branch and the root folder.
5. GitHub Pages will open `index.html`, which forwards visitors to the countdown page.

## Exam Target

The countdown target is set in `outputs/exam-countdown.html`:

```js
const target = new Date("2026-07-15T10:30:00+05:30").getTime();
```
