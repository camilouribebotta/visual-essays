'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

console.log('storiiies.js')

/**
 * Useful tools for working with OpenSeadragon
 * @class
 */
var LookTools = function () {
  /**
   * Instantiating LookTools
   * @param {Object} viewer - The instance of an OpenSeadragon Viewer
   */
  function LookTools(viewer) {
    _classCallCheck(this, LookTools);

    this.viewer = viewer;
    this.imageSize = {
      width: viewer.source.width,
      height: viewer.source.height
    };
    this.containerSize = viewer.viewport.containerSize;
    this.panType = LookTools.getVars().pantype || 'linear';
    this.slowness = LookTools.getVars().slowness || 100;
    this.anno = 0;
    this.img = 0;
    this.stopLookDuration = 5000;
    this.timerTimeout = null;
  }

  /**
   * Static method
   * Retrieve GET params as {key: value} pairs
   * @return {Object} - All GET parameters indexed by name
  */


  _createClass(LookTools, [{
    key: 'goToBounds',


    /**
     * Go to a given position at a given speed
     * @param {Number} - Image cooridate of X position
     * @param {Number} - Image cooridate of Y position
     * @param {Object} - Speed of motion, specified for X and Y
     * @param {Bool} - If True will make shortest movement duration equal to longest movement duration
     */
    value: function goToBounds(targetX, targetY, vArg, elongate) {
      var v = vArg || { x: this.slowness, y: this.slowness };
      var bounds = this.viewer.viewport.getBounds();
      var viewportCoordinates = this.viewer.viewport.imageToViewportCoordinates(targetX, targetY);
      var movement = {
        x: Math.abs(bounds.x - viewportCoordinates.x),
        y: Math.abs(bounds.y - viewportCoordinates.y)
      };

      // If target is out of bounds, adjust
      if (targetX + this.containerSize.x >= this.imageSize.width) {
        movement.x = Math.abs(bounds.x - (this.viewer.viewport.imageToViewportCoordinates(this.imageSize.width, 0).x - bounds.width));
        bounds.x = this.viewer.viewport.imageToViewportCoordinates(this.imageSize.width, 0).x - bounds.width;
      } else {
        bounds.x = viewportCoordinates.x;
      }

      // If target is out of bounds, adjust
      if (targetY + this.containerSize.y >= this.imageSize.height) {
        movement.y = Math.abs(bounds.y - (this.viewer.viewport.imageToViewportCoordinates(0, this.imageSize.height).y - bounds.height));
        bounds.y = this.viewer.viewport.imageToViewportCoordinates(0, this.imageSize.height).y - bounds.height;
      } else {
        bounds.y = viewportCoordinates.y;
      }

      // Setting the animationTime to match that of the longest distance
      if (elongate) {
        var longest = movement.x > movement.y ? movement.x : movement.y;
        this.viewer.viewport.centerSpringX.animationTime = v.x * longest;
        this.viewer.viewport.centerSpringY.animationTime = v.y * longest;
      } else {
        // Setting the animation speed to move at 10px/sec)
        this.viewer.viewport.centerSpringX.animationTime = this.viewer.source.width / 1000 * (this.viewer.source.width / v.x);
        this.viewer.viewport.centerSpringY.animationTime = this.viewer.viewport.containerSize.y / 1000 * (this.viewer.viewport.containerSize.y / v.y);
      }

      this.viewer.viewport.fitBoundsWithConstraints(bounds);
    }

    /**
     * Move the viewport to a target on the X axis.
     * If the viewport is on either extreme, direction is reversed.
     * @param {Object} - The bounding coords of the target
     */

  }, {
    key: 'panX',
    value: function panX(boundsArg) {
      var bounds = boundsArg || this.viewer.viewport.getBounds();
      var targetX = void 0;
      this.panning = 'x';

      // If X is zero go right, else pan left
      if (bounds.x === 0) {
        targetX = this.imageSize.width;
      } else {
        targetX = 0;
      }

      this.goToBounds(targetX, LookTools.imgUnit(this.viewer, { y: bounds.y }));
    }

    /**
     * Move the viewport to a target on the Y axis.
     * If the viewport is on either extreme, directions are reversed.
     * @param {Object} - The bounding coords of the target
     */

  }, {
    key: 'panY',
    value: function panY(boundsArg) {
      var bounds = boundsArg || this.viewer.viewport.getBounds();
      var targetY = void 0;
      this.panning = 'y';
      // As this is linear we always pan down
      targetY = LookTools.imgUnit(this.viewer, { y: bounds.y }) + this.containerSize.y;
      this.goToBounds(LookTools.imgUnit(this.viewer, { x: bounds.x }), targetY);
    }

    /**
     * Move the viewport to a target on the X and Y axis.
     * If the viewport is on either extreme, direction is reversed.
     * @param {Object} - The bounding coords of the target
     */

  }, {
    key: 'panXY',
    value: function panXY(boundsArg) {
      var bounds = boundsArg || this.viewer.getBounds();
      var targetX = void 0;
      var targetY = void 0;

      this.panning = 'xy';

      // Panning X to either left or right
      if (bounds.x === 0) {
        targetX = this.imageSize.width;
      } else {
        targetX = 0;
      }
      // Move 1/3rd of the way down
      targetY = LookTools.imgUnit(this.viewer, { y: bounds.y }) + this.containerSize.y / 2;

      this.goToBounds(targetX, targetY, '', true);
    }

    /**
     * Begin zooming out of the image
     * @param {Object} - The bounding coords of the target (optional)
     */

  }, {
    key: 'initZoom',
    value: function initZoom(target) {
      this.currentAction = 'initZoom';
      // For setting an accurate bounding area when zoomed to maxZoomLevel
      var zoomedWidth = 1 / this.viewer.viewport.maxZoomLevel;
      var bounds = target || this.viewer.viewport.getBounds();

      // Default for no target provided
      if (!target) {
        bounds.width = zoomedWidth;
        bounds.height = zoomedWidth / LookTools.viewportAR(this.viewer);
        bounds.x = 0;
        bounds.y = 0;
      }

      this.viewer.animationTime = 30;
      this.viewer.viewport.animationTime = 30;
      this.viewer.viewport.centerSpringX.springStiffness = 0.01;
      this.viewer.viewport.centerSpringY.springStiffness = 0.01;
      this.viewer.viewport.zoomSpring.springStiffness = 0.01;
      this.viewer.viewport.centerSpringX.animationTime = 0.2 * this.slowness <= 20 ? 0.2 * this.slowness : 20;
      this.viewer.viewport.centerSpringY.animationTime = 0.2 * this.slowness <= 20 ? 0.2 * this.slowness : 20;
      this.viewer.viewport.zoomSpring.animationTime = 0.2 * this.slowness <= 20 ? 0.2 * this.slowness : 20;
      this.viewer.viewport.fitBoundsWithConstraints(bounds);
    }

    /**
     * Look at the region provided
     * @param {Object} - The bounding coords of the target
     */

  }, {
    key: 'lookAt',
    value: function lookAt(target) {
      var current = void 0;
      var currentZoom = void 0;
      var targetZoom = void 0;
      var diff = void 0;
      var longest = void 0;
      this.currentAction = 'moving';
      if (target && typeof target !== 'string') {

        current = this.viewer.viewport.getBounds(true);
        currentZoom = Math.round(1 / current.width);
        targetZoom = Math.round(1 / target.width) < this.viewer.viewport.maxZoomLevel || this.viewer.viewport.maxZoomLevel;
        diff = {
          x: Math.abs(current.x - target.x),
          y: Math.abs(current.y - target.y),
          zoom: Math.abs(currentZoom - targetZoom)
        };
        longest = diff.x > diff.y ? diff.x : diff.y;
        this.viewer.animationTime = 2;
        this.viewer.viewport.animationTime = 2;
        this.viewer.viewport.centerSpringX.springStiffness = 0.01;
        this.viewer.viewport.centerSpringY.springStiffness = 0.01;
        this.viewer.viewport.zoomSpring.springStiffness = 0.01;
        this.viewer.viewport.centerSpringX.animationTime = 5 * longest;
        this.viewer.viewport.centerSpringY.animationTime = 5 * longest;
        this.viewer.viewport.zoomSpring.animationTime = 0.3 * diff.zoom || 0.3;
        var newCurrent = this.viewer.viewport.fitBoundsWithConstraints(target).getBounds();
        newCurrent.x = newCurrent.x.toFixed(4);
        newCurrent.y = newCurrent.y.toFixed(4);
        newCurrent.width = newCurrent.width.toFixed(4);
        newCurrent.height = newCurrent.height.toFixed(4);
        current.x = current.x.toFixed(4);
        current.y = current.y.toFixed(4);
        current.width = current.width.toFixed(4);
        current.height = current.height.toFixed(4);

        // If the previous and next scenes are the same I still want an animation event
        if (JSON.stringify(newCurrent) === JSON.stringify(current)) {
          this.currentAction = 'sameFrame';
          this.viewer.raiseEvent('animation-finish');
        }
      } else {
        console.log('look at whole');
        clearTimeout(this.timerTimeout);
        this.timerTimeout = null;
        this.currentAction = 'moving';
        this.fitToScreen();
      }
    }

    /**
     * Make a highlight overlay over the are provided
     * @param {URL} - A URL with an #xywh fragment
     */

  }, {
    key: 'drawHighlight',
    value: function drawHighlight(url, clickable) {
      var elem = document.createElement('div');
      var _this = this;
      elem.className = 'osd-highlight';
      elem.setAttribute('data-lookat', LookTools.getXywh(this.viewer, url));
      if (clickable) {
        elem.addEventListener('click', function () {
          var xywh = this.getAttribute('data-lookat').split(',');
          _this.viewer.viewport.fitBounds(_this.viewer.viewport.imageToViewportRectangle(xywh[0] | 0, xywh[1] | 0, xywh[2] | 0, xywh[3] | 0));
        });
      }
      this.viewer.addOverlay(elem, LookTools.makeLookatRect(this.viewer, url));
    }

    /**
     * Reset the state of the viewer, removing assets and overlays
     */

  }, {
    key: 'resetState',
    value: function resetState() {
      var resourcesContainer = document.querySelector('#resource-box');
      var overlays = document.querySelectorAll('.osd-highlight');
      var worldItems = this.viewer.world._items;
      var canvas = document.querySelector('canvas');

      canvas.classList.remove('morph');

      if (worldItems.length > 1) {
        while (worldItems.length > 1) {
          this.viewer.world.removeItem(worldItems[worldItems.length - 1]);
        }
        this.viewer.world._items[0].setWidth(1, true);
      }
      // remove overlays
      for (var i = 0; i < overlays.length; i++) {
        this.viewer.removeOverlay(overlays[i]);
      }
    }

    /**
     * Begin zooming out of the image
     */

  }, {
    key: 'exitZoom',
    value: function exitZoom() {
      this.panning = false;
      this.currentAction = 'exitZoom';
      this.fitToScreen();
    }

    /**
     * Set the max zoom level of the image
     */

  }, {
    key: 'setMaxZoom',
    value: function setMaxZoom() {
      // Zoom factor determined by logest side, but will be at least minMaxZoom
      var minMaxZoom = 4;
      var biggest = void 0;
      var zoom = void 0;
      biggest = this.imageSize.width;
      if (this.imageSize.height > biggest) {
        biggest = this.imageSize.height;
      }
      zoom = Math.floor(biggest / 1000);
      this.viewer.viewport.maxZoomLevel = zoom > minMaxZoom ? zoom : minMaxZoom;
    }

    /**
    * Make the viewer fit the image to the screen
    * @param {Boolean} - Fire this immediately
    */

  }, {
    key: 'fitToScreen',
    value: function fitToScreen(immediate) {
      var _this2 = this;

      // If there is no change to make, still fire the animation-finish event
      if (this.viewer.viewport.getBounds(true).y === 0) {
        // this.viewer.raiseEvent('animation-start');
        clearTimeout(this.timerTimeout);
        this.timerTimeout = null;
        if (immediate) {
          this.timerTimeout = setTimeout(function () {
            console.log('raise finish');
            _this2.viewer.raiseEvent('animation-finish');
          }, this.stopLookDuration);
        } else {
          console.log('raise finish');
          this.viewer.raiseEvent('animation-finish');
        }
      } else {
        this.viewer.viewport.fitVertically(immediate);
        this.viewer.raiseEvent('animation-finish');
      }
    }

    /**
    * Does the current image have an annotationList?
    * @param {Object} - The canvas to query against
    */

  }, {
    key: 'getAnnotationList',
    value: function getAnnotationList(canvas) {
      if (canvas.annotationList) {
        return canvas.annotationList.resources;
      } else {
        return [];
      }
    }

    /**
    * Create a timed event
    * @param {Function} - A function to be the timeout callback
    * @param {Integer} - Optional override for time to wait before callback
    */

  }, {
    key: 'timer',
    value: function timer(callback, delay) {
      delay = delay || this.stopLookDuration;
      clearTimeout(this.timerTimeout);
      this.timerTimeout = null;
      this.timerTimeout = setTimeout(callback, delay);
    }

    /**
    * Update the page
    */

  }, {
    key: 'updatePage',
    value: function updatePage() {
      if (this.viewer.tileSources.length > 1 && this.img < this.viewer.tileSources.length - 1) {
        console.log('go to next page');
        this.img += 1;
      } else {
        console.log('just start again');
        this.img = 0;
      }
      this.currentAction = 'pageChange';
      this.viewer.raiseEvent('animation-finish');
    }
  }], [{
    key: 'getVars',
    value: function getVars() {
      var vars = {};
      var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
      });
      return vars;
    }

    /**
     * Static method
     * Aspect ratio of the image
     * @param {Object} - OpenSeadragon Viewer
     * @return {Number} - Image aspect ratio
     */

  }, {
    key: 'imageAR',
    value: function imageAR(viewer) {
      return viewer.source.width / viewer.source.height;
    }

    /**
     * Static method
     * Aspect ratio of the viewport
     * @param {Object} - OpenSeadragon Viewer
     * @return {Number} - Viewport aspect ratio
     */

  }, {
    key: 'viewportAR',
    value: function viewportAR(viewer) {
      return viewer.viewport.getAspectRatio();
    }

    /**
     * Static method
     * Get a single value from a viewport coord as an image coord
     * @param {Object} - OpenSeadragon Viewer
     * @param {Number} - The value to be converted to image co-ordinates
     * @return {Number} - The image co-ordinates of value param
     */

  }, {
    key: 'imgUnit',
    value: function imgUnit(viewer, value) {
      var unit = void 0;
      if (typeof value.x !== 'undefined') {
        unit = viewer.viewport.viewportToImageCoordinates(value.x, 0).x;
      } else if (typeof value.y !== 'undefined') {
        unit = viewer.viewport.viewportToImageCoordinates(0, value.y).y;
      }
      return unit;
    }

    /**
     * Static method
     * Take a string of x,y,w,h values and return the viewport co-ordinates
     * @param {String} - OpenSeadragon Viewer
     * @param {String} - The values to be converted to viewport co-ordinates
     * @return {Object} - Viewport Rectangle object
     */

  }, {
    key: 'getCoords',
    value: function getCoords(viewer, string) {
      var xywh = string.split(',');
      // X/Y are top left, so point is + 50% of W/H
      var point = new OpenSeadragon.Point(parseInt(xywh[0], 10) + parseInt(xywh[2], 10) / 2, parseInt(xywh[1], 10) + parseInt(xywh[3], 10) / 2);
      return viewer.viewport.imageToViewportCoordinates(point);
    }

    /**
     * Static method
     * Has the viewer reached the bottom edge of the image
     * @param {Object} - OpenSeadragon Viewer
     * @return {Bool} - True if the viewer has reached the bottom edge of the image
     */

  }, {
    key: 'isAtBottom',
    value: function isAtBottom(viewer) {
      var bounds = viewer.viewport.getBounds();
      var computedY = LookTools.imgUnit(viewer, { y: bounds.y }) + LookTools.imgUnit(viewer, { y: bounds.height });
      var roundedY = computedY << 0;
      roundedY = roundedY === computedY ? roundedY : roundedY + 1;

      if (roundedY < viewer.source.height) {
        return false;
      } else {
        return true;
      }
    }

    /**
     * Static method
     * Make a viewport rectangle from a given URL with XYWH fragment
     * @param {Object} - The viewer
     * @param {String} - The url with XYWH fragment
     * @return {Array} - XYWH values
     */

  }, {
    key: 'makeLookatRect',
    value: function makeLookatRect(viewer, url) {
      // This has nothing to do with viewport or container size, but more the relative size
      // (h/w) of the crop from the source ala IIIF
      // This is why getCoords works based on fixed values from the crop
      var target = void 0;
      if (typeof url === 'string') {
        var xywh = LookTools.getXywh(viewer, url);
        if (xywh !== 'zoomOut') {
          return viewer.viewport.imageToViewportRectangle(xywh[0] | 0, xywh[1] | 0, xywh[2] | 0, xywh[3] | 0);
        } else {
          return xywh;
        }
      }
    }

    /**
     * Static method
     * Get XYWH values from a provided URL with and XYWH fragment
     * @param {Object} - The viewer
     * @param {String} - The url with XYWH fragment
     * @return {Array} - XYWH values
     */

  }, {
    key: 'getXywh',
    value: function getXywh(viewer, url) {
      var xywh = void 0;
      var fragment = void 0;
      if (typeof url === 'string') {
        fragment = url.split('#xywh=');
        if (fragment[1]) {
          xywh = fragment[1].split(',');
        } else {
          // If fragment is not provided, return zoomOut
          xywh = 'zoomOut';
        }
        return xywh;
      }
    }

    /**
     * Static method
     * Pull otu descriptive data from a given resource Object
     * @param {Object} - Resource object containing decriptive data
     */

  }, {
    key: 'getDescription',
    value: function getDescription(resource) {
      // Will either be a type of description, or inline as 'chars'
      return resource.description ? resource.description : resource.chars;
    }

    /**
     * Static method
     * Gets the amout of time in milliseconds a pieace of text should take to read
     * @param {Object} - Resource object containing decriptive data
     */

  }, {
    key: 'getReadTime',
    value: function getReadTime(resource) {
      // Will either be a type of description, or inline as 'chars'
      var string = resource.description ? resource.description : resource.chars;
      return string.split(' ').length / 4;
    }
  }]);

  return LookTools;
}();

var lookTools = void 0;
var viewer = void 0;

document.addEventListener('DOMContentLoaded', function () {
console.log('storiiies: DOMContentLoaded')
/*  var manifest = 'https://jqz7t23pp9.execute-api.us-east-1.amazonaws.com/dev/manifest/' + window.location.href.split('/viewer/')[1].split('?')[0].split('/')[0] + '/manifest.json';
  fetch(window.location.origin + '/manifestJSON?manifest=' + manifest).then(function (res) {
    res.json().then(function (data) {
      addSourceInfoToDL(data);
      initialiseViewer(data);
    }).catch(function (err) {
      throw err;
    });
  }).catch(function (err) {
    document.write(err);
  });
  */
});

// Push source data to dataLayer for use in GTM
function addSourceInfoToDL(data) {
  // send source url
  window.dataLayer.push({
    "event": "storyViewed",
    "imageSource": data['sequences'][0]['canvases'][0]['images'][0]['resource']['@id']
  });
}

function initialiseViewer(data) {
  var annotationDiv = document.querySelector('#annotation');
  var annotationList = void 0;
  var canvases = data['sequences'][0]['canvases'];
  var captionBox = document.querySelector('.caption-box');
  var hideButton = document.querySelector('#caption-box-hide');
  var showButton = document.querySelector('#caption-box-show');

  // Set document title to name of story
  var storyTitle = data['label']['@value'];
  document.title = storyTitle + ' - Storiiies by Cogapp';

  viewer = OpenSeadragon({
    id: 'osd-viewer',
    prefixUrl: '/vendor/openseadragon/images/',
    minZoomLevel: 0,
    defaultZoomLevel: 0,
    sequenceMode: true,
    visibilityRatio: 0.2,
    tileSources: data['sequences'][0]['pages'],
    showNavigationControl: false,
    showZoomControl: false,
    showSequenceControl: false,
    showRotationControl: false,
    showFullPageControl: false
  });

  viewer.addHandler('open', function () {
    // Initialise look tools
    lookTools = lookTools || new LookTools(viewer);

    // Get annotationList for current image (or [])
    annotationList = lookTools.getAnnotationList(canvases[lookTools.img]);

    // Set the zoomLevel based on current image
    lookTools.setMaxZoom();

    // Set the image to fit to the screen
    lookTools.fitToScreen(true);

    // Show opening labels
    annotationDiv.classList.remove('hidden');
    lookTools.anno = -1;
    annotationDiv.innerText = canvases[lookTools.img]['label']['@value'];

    // GTM: Send 'viewed' event to dataLayer
    window.dataLayer.push({
      "event": "viewerViewed",
      "annotationText": LookTools.getDescription(annotationList[lookTools.anno]['resource'])
    });
  });

  viewer.addHandler('page', function (e) {
    // Get annotationList for current image (or [])
    annotationList = lookTools.getAnnotationList(canvases[lookTools.img]);

    lookTools.anno = -1;
    annotationDiv.innerText = canvases[e.page]['label']['@value'];
  });

  viewer.addHandler('animation-finish', function (e) {
    // Settings for more pleasant dragging
    viewer.viewport.zoomSpring.animationTime = 1.2;
    viewer.viewport.centerSpringX.animationTime = 1.2;
    viewer.viewport.centerSpringY.animationTime = 1.2;
    viewer.viewport.zoomSpring.springStiffness = 6.5;
    viewer.viewport.centerSpringX.springStiffness = 6.5;
    viewer.viewport.centerSpringY.springStiffness = 6.5;
  });

  document.querySelector('#next').addEventListener('click', function () {
    if (annotationList.length) {
      if (lookTools.anno < annotationList.length - 1) {
        lookTools.anno += 1;
        goToAnnotation();
      } else {
        lookTools.anno = -1;
        if (canvases.length > 1 && lookTools.img < canvases.length - 1) {
          lookTools.img += 1;
        } else {
          lookTools.img = 0;
        }
        viewer.goToPage(lookTools.img);
      }
    } else {
      if (canvases.length > 1 && lookTools.img < canvases.length - 1) {
        lookTools.img += 1;
      } else {
        lookTools.img = 0;
      }
      viewer.goToPage(lookTools.img);
    }
  });

  document.querySelector('#previous').addEventListener('click', function () {
    if (annotationList.length) {
      if (lookTools.anno >= 0) {
        lookTools.anno -= 1;
        if (lookTools.anno === -1) {
          lookTools.fitToScreen();
          annotationDiv.innerText = canvases[lookTools.img]['label']['@value'];
        } else {
          goToAnnotation();
        }
      } else {
        lookTools.anno = -1;
        if (canvases.length > 1) {
          if (lookTools.img >= 1) {
            lookTools.img -= 1;
          } else {
            lookTools.img = canvases.length - 1;
          }
          viewer.goToPage(lookTools.img);
        }
      }
    } else {
      if (canvases.length > 1 && lookTools.img >= 1) {
        lookTools.img -= 1;
      } else {
        lookTools.img = canvases.length - 1;
      }
      viewer.goToPage(lookTools.img);
    }
  });

  hideButton.addEventListener('click', function () {
    captionBox.classList.add('caption-box--hidden');
    showButton.classList.add('caption-box-show--show');
  });

  showButton.addEventListener('click', function () {
    captionBox.classList.remove('caption-box--hidden');
    showButton.classList.remove('caption-box-show--show');
  });

  function setAnnotationContent(resource) {
    annotationDiv.innerHTML = '';
    var firstAudio = true;

    function appendAudio(src) {
      var autoplay = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;

      var audioElem = document.createElement('audio');
      audioElem.className = 'annotation-audio';
      audioElem.controls = true;
      audioElem.autoplay = autoplay;
      audioElem.src = src;
      annotationDiv.appendChild(audioElem);
    }

    if (resource['@type'] === 'cnt:ContentAsText') {
      annotationDiv.innerText = LookTools.getDescription(resource);
    }
    if (resource['@type'] === 'dctypes:Sound') {
      appendAudio(resource['@id']);
    }
    // Generally assumes composite is audio(s) + text
    else if (resource['@type'] === 'oa:Composite') {
        annotationDiv.innerText = LookTools.getDescription(resource['default']);
        if (resource['item']) {
          for (var i = 0; i < resource['item'].length; i++) {
            if (resource['item'][i]['@type'] === 'dctypes:Sound') {
              appendAudio(resource['item'][i]['@id'], firstAudio);
              firstAudio = false;
            }
          }
        }
      }
  }

  // Update the view based on an annotation
  function goToAnnotation() {
    var resourcesContainer = document.querySelector('#resource-box');
    var annotation = annotationList[lookTools.anno];
    var resource = annotation['resource'];
    var highlights = void 0;
    var lookat = void 0;
    var zoomedWidth = 1 / viewer.viewport.maxZoomLevel;
    lookTools.resetState();

    viewer.viewport.zoomSpring.animationTime = 2.8;
    viewer.viewport.centerSpringX.animationTime = 2.8;
    viewer.viewport.centerSpringY.animationTime = 2.8;

    // Update the text description of the annotation
    lookat = annotationList[lookTools.anno]['on'];

    setAnnotationContent(resource);

    // Show media if necessary
    if (resource['@id']) {
      // An image
      if (resource['@type'] === 'dctypes:Image') {
        viewer.world._items[lookTools.img].setWidth(0.75);

        viewer.addSimpleImage({
          url: resource['@id'],
          width: 0.25,
          x: 0.75
        });

        setTimeout(function () {
          window.viewer.viewport.fitVertically();
        }, 500);
      }
    }

    // Could be an array for highlighting
    if ((typeof lookat === 'undefined' ? 'undefined' : _typeof(lookat)) === 'object') {
      window.viewer.viewport.goHome();
      // Highlight regions
      for (var i = 0; i < lookat.length; i++) {
        lookTools.drawHighlight(lookat[i], true);
      }
    } else {
      var target = LookTools.makeLookatRect(viewer, lookat);
      if (typeof target !== 'string') {
        // fitBounds to the lookat coords
        viewer.viewport.fitBounds(target);
      }
    }

    // Push custom event to dataLayer to indicate when a new annotation is shown
    window.dataLayer.push({
      "event": "annotationRead",
      "annotationTotal": annotationList.length + 1, // Add 1 to make 1-based index
      "currentAnnotation": lookTools.anno + 1 // Add 1 to make 1-based index
    });
  }

  document.body.addEventListener('click', function (e) {
    if (e.target.id === 'transform') {
      document.querySelector('canvas').classList.toggle('morph');
    }
  });

  document.body.addEventListener('click', function (e) {
    if (e.target.id === 'transform') {
      document.querySelector('canvas').classList.toggle('morph');
    }
  });
}
//# sourceMappingURL=shortcode.js.map
