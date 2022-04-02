## Front App

- Front application using [React](https://reactjs.org/) framework and [Tableau JavaScript API](https://help.tableau.com/current/api/js_api/en-us/JavaScriptAPI/js_api.htm).
- Credit to [andre347's](https://github.com/andre347) tutorials

## Setup

Install [Nvm](https://github.com/nvm-sh/nvm) and Node 
```
$ curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
$ nvm install 16.14.2
$ nvm unalias default
$ nvm alias default 16.14.2
$ node -v
v16.14.2
```

Install packages
```
$ npm install
```

Run
```
$ npm run start
```

Test
```
$ npm run test
```

Build and deploy with a commit message to `gh-pages` branch
```
$ npm run deploy -- -m "Deploy React app to GitHub Pages"
$ 
```