import { fetchDataAtFixedInterval, resizeViz, debounce } from './helpers';

jest.useFakeTimers();

describe('Helpers', () => {
  describe('fetchDataAtFixedInterval', () => {
    const viz = {
      refreshDataAsync: jest.fn(),
    };

    afterEach(() => {
      jest.clearAllTimers();
      jest.clearAllMocks();
    });

    it('should not call setInterval before 5 seconds', () => {
      fetchDataAtFixedInterval(viz);
      expect(viz.refreshDataAsync).not.toBeCalled();
    });

    describe('should call refreshDataAsync every 5 seconds', () => {
      it('after 5 seconds', () => {
        fetchDataAtFixedInterval(viz);      
        jest.advanceTimersByTime(5000);
        expect(viz.refreshDataAsync).toHaveBeenCalledTimes(1);
      });

      it('after 10 seconds', () => {
        fetchDataAtFixedInterval(viz);      
        jest.advanceTimersByTime(10000);
        expect(viz.refreshDataAsync).toHaveBeenCalledTimes(2);
      });

      it('after 15 seconds', () => {
        fetchDataAtFixedInterval(viz);      
        jest.advanceTimersByTime(15000);
        expect(viz.refreshDataAsync).toHaveBeenCalledTimes(3);
      });
    });
  });

  describe('resizeViz', () => {
    const viz = {
      setFrameSize: jest.fn(),
    };

    it('should call setFrameSize with width and height', () => {
      const width = 800;
      const height = 600;

      resizeViz(viz, width, height);
      expect(viz.setFrameSize).toHaveBeenCalledWith(width, height);
    });
  });
});