# Salzberg Weekly Plan

An 800×480 family plan for the reTerminal E1002 (6-color E Ink Spectra 6), shown through SenseCraft HMI.

**Display image:** https://raw.githubusercontent.com/salzcode/familyplan/display/plan.png

The page reads the family Google Sheet, **Salzberg Weekly Family Plan**, every time the display refreshes. To change what's shown, just edit the Sheet.

## How it reads the Sheet

- **Tab:** the first tab that has a `Child` header row. Put the current week's tab first, leftmost.
- **Days:** the day columns (`Monday` … `Friday`). Hidden columns and hidden rows are skipped.
- **Kids:** each kid's rows are the ones under their name in column A. The `Item` text (To school, Home + time, Afterschool) picks the little picture; the item name itself isn't shown. Blank, `—` and blacked-out cells are hidden.
- **Times:** a time in a cell (`6 pm`, `5:30-6`, `2:30ish`) moves to the column on the right.
- **Drivers:** the cell **color** is matched to the sheet's **Legend** row. If a cell's color isn't in the legend, the page looks for a name in the text instead (for example, "Navit"). A black cell means "not applicable". The "Needs to be figured out" color, or a `?` in the text, makes the row yellow. `NO SCHOOL` shows white text on black.
- **Family dinner** and the **Ori/Navit Night Activity** row appear in the green dinner bar.
- **Pictures:** the activity picture comes from keywords: soccer, music, guitar, dance, boxing, math, tutoring, drama/rehearsal, CLUE, swim, basketball. The dinner picture also comes from keywords: schnitzel, grill, sushi, salmon/fish, pizza, pasta, tacos, burger, Sukkot, Shabbat/holiday. Anything else gets a star or a plate.
- **Timing:** the page uses Eastern time. From 7 pm on it shows tomorrow, and on weekends it shows the next school day.

Settings are at the top of the script in `index.html`: `PEOPLE` (the badge color for each driver), `HELPERS` (other grown-ups who get a white badge), `KID_COLORS`, `TAB`, and `ROLLOVER_HOUR`.

The Sheet must stay shared as **Anyone with the link → Viewer**.

## Photos

The right side shows a photo from the shared Google Photos album, changing every hour. Only portrait photos that already fit the box are used, so nothing gets awkwardly cropped. To change the album, edit `ALBUM` in `photo.py`.

## Shabbat

From an hour before candle lighting until havdalah, the display switches to a full-screen landscape photo from the album with a "Shabbat Shalom" box: the parasha, candle lighting and havdalah. The times come from Hebcal for Atlanta; change `HEBCAL_GEONAMEID` in `photo.py` for another city, and `SHABBAT_LEAD_MIN` in `index.html` to change the lead time.

## SenseCraft HMI

The GitHub Action **Render display image** runs every 15 minutes. It picks a photo, screenshots the page at 800×480, snaps it to the six colors, and publishes the result to:

`https://raw.githubusercontent.com/salzcode/familyplan/display/plan.png`

In SenseCraft, the **New Canvas** design has a full-screen Image element that points at that URL. That design is assigned to Salzberg Display 1.

`week.html` is the older Tue–Fri grid. It isn't connected to the Sheet.
