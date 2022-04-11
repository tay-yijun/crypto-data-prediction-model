export const fetchDataAtFixedInterval = (viz, interval = 5000) => {
  setInterval(() => {
    viz.refreshDataAsync();

    const intervalInSeconds = new Date(interval).getSeconds();
    const date = Date.now();
    const dateFormatted = new Date(date).toLocaleTimeString();

    console.log(`Refresh - ${intervalInSeconds} second interval - ${dateFormatted}`);
  }, interval);
};

export const resizeViz = (viz, width, height) => {
  console.log(`Resize - width: ${width} height: ${height}`);
  viz.setFrameSize(width, height);
};
