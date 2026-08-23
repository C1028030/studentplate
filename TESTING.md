# StudentPlate Prototype Testing

## Testing overview

StudentPlate was tested throughout development using manual functional, usability, responsive and accessibility testing. Problems found during testing were corrected and tested again.

## Recommendation testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| No saved preferences | The user is directed to set their preferences | A setup message and link to the preferences page were displayed | Pass |
| Balanced recommendations | Affordable meals matching the selected price and time are displayed | Matching meals were returned and ordered by affordability | Pass |
| Vegetarian preference | Only vegetarian and vegan meals are displayed | Standard meals were excluded while vegetarian and vegan meals remained | Pass |
| Vegan preference | Only vegan meals are displayed | Only meals classified as vegan were returned | Pass |
| Higher-protein goal | Recommended meals contain at least 25g protein | Meals below 25g protein were excluded | Pass |
| Maximum price | Meals above the selected price are excluded | All displayed meals were within the maximum price | Pass |
| Maximum preparation time | Meals exceeding the selected time are excluded | All displayed meals were within the selected preparation time | Pass |
| No matching meals | A helpful empty state is displayed | A message suggested changing preferences or browsing all meals | Pass |
| Unavailable meal | Unavailable meals are excluded | The meal disappeared after being marked unavailable in Django Admin | Pass |
| Recommendation explanation | Each result explains why it matched | Cost, time, dietary type and protein were displayed where relevant | Pass |

## Catalogue testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| Search by meal name | Relevant meal is displayed | Searching for meal names returned the correct results | Pass |
| Search by description | Meals containing matching description text are displayed | Relevant description matches were returned | Pass |
| Category filter | Only meals in the selected category are displayed | Other meal categories were excluded | Pass |
| Maximum-price filter | Meals above the entered price are excluded | Only meals within the price limit appeared | Pass |
| Preparation-time filter | Meals exceeding the selected time are excluded | Only meals within the time limit appeared | Pass |
| Combined filters | All active filters are applied together | Results matched the search, category, price and time selections | Pass |
| No catalogue results | A useful empty state is displayed | A no-results message and clear-filters option appeared | Pass |
| Clear filters | Complete catalogue is restored | All meals appeared after filters were cleared | Pass |

## Budget testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| Daily-budget calculation | Weekly budget is divided by seven | A £25 budget produced a daily allowance of £3.57 | Pass |
| Budget slider | Slider and number input remain synchronised | Moving the slider updated the input and daily allowance | Pass |
| Save weekly budget | Budget remains available after navigation | The value remained stored using the Django session | Pass |
| Invalid low budget | Values below the permitted range are rejected | An appropriate validation message was displayed | Pass |
| Invalid high budget | Values above the permitted range are rejected | An appropriate validation message was displayed | Pass |

## Planner testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| Add meal to planner | Meal appears on the selected day | The selected meal and day appeared on the planner page | Pass |
| Duplicate meal and day | Exact duplicate is prevented | Adding the same meal to the same day did not create another entry | Pass |
| Same meal on different days | Meal can be planned on multiple days | The same meal appeared correctly on different selected days | Pass |
| Remove planned meal | Only the selected entry is removed | The original removal logic failed, but was corrected and retested successfully | Fixed and retested |
| Planner cost | Prices of all planned meals are totalled | Total cost updated when meals were added or removed | Pass |
| Planner calories | Calories from all planned meals are totalled | The displayed calorie total matched the selected meals | Pass |
| Planner protein | Protein from all planned meals is totalled | The displayed protein total matched the selected meals | Pass |
| Remaining budget | Remaining amount is calculated correctly | Planned cost was subtracted from the saved weekly budget | Pass |
| Over-budget status | Overspending is clearly highlighted | The colour styling initially failed, but the conditional class was corrected and retested | Fixed and retested |
| Empty planner | Helpful empty state is displayed | A message and link to find meals appeared | Pass |

## Favourites testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| Save favourite | Meal appears on the favourites page | The selected meal was stored in the session and displayed | Pass |
| Prevent duplicate favourite | Meal appears only once | Saving the same meal again did not create a duplicate | Pass |
| Remove from meal page | Favourite is removed while remaining on the meal page | The meal was removed and the button returned to its unsaved state | Pass |
| Remove from favourites page | Meal is removed while remaining on Favourites | The selected meal disappeared from the favourites page | Pass |
| Empty favourites | Helpful empty state is displayed | A message and link to find meals appeared | Pass |
| Unavailable favourite | Unavailable meal is not displayed | The unavailable record was excluded | Pass |

## Progress dashboard testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| Planned-meal count | Count matches the planner | Dashboard count matched the current planner entries | Pass |
| Days-planned count | Unique planned days are counted | Multiple meals on one day did not incorrectly increase the day count | Pass |
| Favourite count | Count matches Favourites | Dashboard count matched the saved favourite meals | Pass |
| Planned cost | Cost matches planner total | The dashboard and planner displayed the same value | Pass |
| Nutritional totals | Calories and protein match the planner | Both totals matched the selected planner meals | Pass |
| Within-budget state | Sufficient budget is shown in green | Remaining budget appeared using the green status panel | Pass |
| Over-budget state | Overspending is shown in red | Overspending appeared using the red status panel | Pass |
| No saved budget | Setup prompt is displayed | A message and link to the budget page appeared | Pass |

## Usability and accessibility testing

| Test | Expected result | Actual result | Status |
| --- | --- | --- | --- |
| Keyboard navigation | All interactive controls are accessible using Tab | Links, buttons, form fields and selectors could be reached | Pass |
| Skip link | Skip link appears on keyboard focus | The link was initially missed because the page required refreshing, then worked correctly | Fixed and retested |
| Skip-link destination | Activating the link bypasses navigation | Focus moved to the main page content | Pass |
| Focus indicators | Focused controls have a visible outline | A yellow outline appeared around the focused controls | Pass |
| Active navigation | Current page is identified | The relevant navigation link was underlined and marked as current | Pass |
| Form labels | Inputs have visible, descriptive labels | Budget, filter, preference and planner controls were labelled | Pass |
| Error messages | Errors are visible and accessible | Validation messages were displayed using an alert role | Pass |
| Success messages | Confirmation is visible and accessible | Successful budget and preference saves displayed confirmation | Pass |
| Mobile layout | Content adapts without horizontal scrolling | Cards and forms stacked at smaller browser widths | Pass |
| Empty states | Empty pages provide useful next actions | Catalogue, planner, favourites and recommendations provided relevant links | Pass |

## Technical testing and issues resolved

Several implementation issues were identified during development:

- A misspelled `urlpatterns` variable prevented Django from loading application routes.
- An accidental nested Django project folder caused the wrong settings and URL files to be edited.
- Template paths were corrected where `meal_list.html` had been misspelled.
- Django template variables were corrected where spaces were used instead of underscores.
- CSS rules were moved outside mobile media queries where desktop styling was not being applied.
- Duplicate planner forms were removed from the meal-detail page.
- Planner session keys and form-field names were made consistent.
- Planner removal logic was rewritten and successfully retested.
- Conditional budget-status classes were corrected so overspending appeared in red.
- Browser stylesheet versions were updated to prevent cached CSS from hiding changes.

## Final outcome

The prototype successfully supports the intended core user journey:

1. Set a weekly food budget.
2. Save dietary, cost, time and health preferences.
3. Receive personalised meal recommendations.
4. Search and filter the complete meal catalogue.
5. View meal cost and nutritional information.
6. Save favourite meals.
7. Add meals to a weekly planner.
8. Review planned spending and nutritional totals.
9. Compare planned spending with the saved budget.

All identified functional and interface issues were corrected and retested.