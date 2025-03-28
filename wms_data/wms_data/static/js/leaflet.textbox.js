(function () {

    var __onAdd = L.Rectangle.prototype.onAdd,
        __onRemove = L.Rectangle.prototype.onRemove,
        __updatePath = L.Rectangle.prototype._updatePath,
        __bringToFront = L.Rectangle.prototype.bringToFront;
    
    var TextBox = {
        onAdd: function (map) {
            __onAdd.call(this, map);
            this._textRedraw();
        },
    
        onRemove: function (map) {
            map = map || this._map;
            this.setText(null);
            __onRemove.call(this, map);
        },
    
        bringToFront: function () {
            __bringToFront.call(this);
            this._textRedraw();
        },
    
        _updatePath: function () {
            __updatePath.call(this);
            this._textRedraw();
        },
    
        _textRedraw: function () {
            var text = this._text,
                options = this._textOptions;
            if (text) {
                this.setText(null);
                this.setText(text, options);
            }
        },

        calculateRectangleRotationAngle: function (nw, ne, sw, se) {
            // Tính tâm của hình chữ nhật
            let centerX = (ne.x + sw.x) / 2;
            let centerY = (ne.y + sw.y) / 2;
        
            // Tính góc quay bằng arctan từ NW -> NE
            let deltaX = ne.x - nw.x;
            let deltaY = ne.y - nw.y;
            let angleRad = Math.atan2(deltaY, deltaX); // Góc tính bằng radian
            let angleDeg = angleRad * (180 / Math.PI); // Chuyển sang độ
        
            return {
                center: { x: centerX, y: centerY },
                rotationAngle: angleDeg
            };
        },
    
        setText: function (text, options) {
            this._text = text;
            this._textOptions = options;
            this.options.text = text;
            this.options.textOptions = options;
    
            // If not in SVG mode or Rectangle not added to map yet return
            // setText will be called by onAdd, using value stored in this._text
            if (!L.Browser.svg || typeof this._map === 'undefined') {
              return;
            }
    
            // Figure out the options, taking into account the defaults
            var defaults = {
            };
            options = L.Util.extend(defaults, options);
    
            // Get the SVG container element
            var svg = this._map.getRenderer(this)._container;
    
            // If empty text, hide and return
            if (!text) {
                if (this._textNode && this._textNode.parentNode) {
                    svg.removeChild(this._textNode);
    
                    // Delete the node, so it will not be removed a 2nd time if the layer is later removed from the map
                    delete this._textNode;
                }
                return;
            }
    
            // Add non-breakable spaces to the text
            text = text.replace(/ /g, '\u00A0');
    
            // Add the id to the path
            var id = 'textbox-' + L.Util.stamp(this);
            this._path.setAttribute('id', id);
    
            // Create the text node
            var textNode = L.SVG.create('text');
            textNode.setAttributeNS("http://www.w3.org/1999/xlink", "xlink:href", '#' + id);
            this._textNode = textNode;
            svg.appendChild(textNode);
    
            // Get the position of the text node
            var northWest = this.getBounds().getNorthWest();
            var southEast = this.getBounds().getSouthEast();
            var northEast = this.getBounds().getNorthEast();
            var southWest = this.getBounds().getSouthWest();
            var northWestPoint = this._map.latLngToLayerPoint(northWest);
            var southEastPoint = this._map.latLngToLayerPoint(southEast);
            var northEastPoint = this._map.latLngToLayerPoint(northEast);
            var southWestPoint = this._map.latLngToLayerPoint(southWest);

            var rect_info = this.calculateRectangleRotationAngle(northWestPoint, northEastPoint, southWestPoint, southEastPoint)

            console.log(this)

            var width = southEastPoint.x - northWestPoint.x;
            textNode.setAttribute('x', northWestPoint.x);
            textNode.setAttribute('y', northWestPoint.y);
            textNode.setAttribute('transform', `rotate(${rect_info.rotationAngle} ${rect_info.center.x} ${rect_info.center.y})`);
    
            // Calculate the scale of the text
            var defaultScale = 13;
            var offsetFromDefault = this._map.getZoom() - 13 //+ parseInt((this.options.textOptions?.fontSize || 0))
            var twoToPowerOfOffset = Math.pow(2, offsetFromDefault)
    
            // Create the the inner spans
            var words = text.split(/\s+/).reverse(),
                word,
                line = [],
                lineNumber = 0,
                lineHeight = 1.1, // em
                tspan = L.SVG.create('tspan');
            tspan.setAttribute('style', 'font: ' +  (this.options.textOptions?.style || "normal") + ' ' + twoToPowerOfOffset + 'em ' + (this.options.textOptions?.font || "arial"));
            tspan.setAttribute('fill', this.options.textOptions?.color || '#000000');
            tspan.setAttribute('x', textNode.getAttribute('x'));
            tspan.setAttribute('y', textNode.getAttribute('y'));
            tspan.setAttribute('dy', ++lineNumber * lineHeight + "em");
            textNode.appendChild(tspan);
            while (word = words.pop()) {
                line.push(word);
                tspan.innerHTML = line.join(" ");
                if (tspan.getComputedTextLength() > width) {
                    // Remove the last word which overflowed
                    line.pop();
                    tspan.innerHTML = line.join(" ");
                    // Add the word to the new line
                    line = [word];
                    // Start a new tspan
                    tspan = L.SVG.create('tspan');
                    tspan.setAttribute('style', 'font: ' +  (this.options.textOptions?.style || "normal") + ' ' + twoToPowerOfOffset + 'em ' + (this.options.textOptions?.font || "arial"));
                    tspan.setAttribute('fill', this.options.textOptions?.color || '#000000');
                    tspan.setAttribute('x', textNode.getAttribute('x'));
                    tspan.setAttribute('y', textNode.getAttribute('y'));
                    tspan.setAttribute('dy', ++lineNumber * lineHeight + "em");
                    textNode.appendChild(tspan);
                    tspan.innerHTML = line.join(" ");
                }
            }
    
            return;
        }
    };
    
    L.Rectangle.include(TextBox);
    
    L.LayerGroup.include({
        setText: function(text, options) {
            for (var layer in this._layers) {
                if (typeof this._layers[layer].setText === 'function') {
                    this._layers[layer].setText(text, options);
                }
            }
            return;
        }
    });
    
    })();