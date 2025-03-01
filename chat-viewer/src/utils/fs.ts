import { results as data } from "../../../evaluation_results.json"

window.fs = {
  readFile: async () => JSON.stringify(data),
};
