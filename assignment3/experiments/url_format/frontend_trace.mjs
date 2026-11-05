// Local JS checks only; URL() parses text and never requests a website.
import { validateURL, sessionEntry } from '../../frontend/src/validation.js';
const cases = ['https://www.google.com/','www.google.com/','https://github.com/','github.com/'];
const checks = cases.map(url => ({url, validation:validateURL(url), submittedVerbatim:validateURL(url)==='' ? url : null}));
const presentation = [0.972174377884553,0.18655881540261557].map(p => {
  const predicted_class=Number(p>=.5);
  const response={predicted_class,dangerous_probability:p,confidence:predicted_class?p:1-p,label:predicted_class?'Potentially dangerous':'Likely legitimate',signals:[]};
  return {api:response, session:sessionEntry(response,1)};
});
console.log(JSON.stringify({checks,presentation,notes:'App.jsx serialises submittedURL = draft, sends JSON {url:submittedURL}; Result.jsx renders the API label and confidence. The validation URL() is not assigned back to the input.'},null,2));
