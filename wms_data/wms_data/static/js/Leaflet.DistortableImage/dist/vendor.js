function dataURItoBlob(t) {
    for (var e = (0 <= t.split(",")[0].indexOf("base64") ? atob : unescape)(t.split(",")[1]), r = (t = t.split(",")[0].split(":")[1].split(";")[0],
    new Uint8Array(e.length)), o = 0; o < e.length; o++)
        r[o] = e.charCodeAt(o);
    return new Blob([r],{
        type: t
    })
}
function canvasToBlobUrl(t) {
    return t = dataURItoBlob(t.toDataURL("image/png")),
    window.URL.createObjectURL(t)
}
function warpWebGl(t, e, r, o) {
    try {
        var i = fx.canvas(1500, 1500)
    } catch (t) {
        return void alert(t)
    }
    var a = document.getElementById(t)
      , n = new Image;
    n.onload = function() {
        for (var t = i.texture(n), l = (e[0],
        e[1],
        e[2],
        e[3],
        e[4],
        e[5],
        e[6],
        e[7],
        r[0],
        r[1],
        r[2],
        r[3],
        r[4],
        r[5],
        r[6],
        r[7],
        []), s = [], c = 0; c < e.length; c += 2)
            l.push(e[c]);
        for (c = 1; c < e.length; c += 2)
            s.push(e[c]);
        var u = Math.min.apply(null, s)
          , h = (matrix1southmost = Math.max.apply(null, s),
        matrix1westmost = Math.min.apply(null, l),
        matrix1eastmost = Math.max.apply(null, l),
        [])
          , f = [];
        for (c = 0; c < r.length; c += 2)
            h.push(r[c]);
        for (c = 1; c < r.length; c += 2)
            f.push(r[c]);
        var d = Math.min.apply(null, f)
          , m = (matrix2southmost = Math.max.apply(null, f),
        matrix2westmost = Math.min.apply(null, h),
        matrix2eastmost = Math.max.apply(null, h),
        matrix2westmost - matrix1westmost)
          , g = d - u
          , p = (i.draw(t, n.width, n.height),
        t = (matrix2southmost - d) / (matrix1southmost - u),
        d = (matrix2eastmost - matrix2westmost) / (matrix1eastmost - matrix1westmost),
        Math.max(d, t));
        for (c = 0; c < r.length; c += 2)
            r[c] -= m,
            r[c] /= p;
        for (c = 1; c < r.length; c += 2)
            r[c] -= g,
            r[c] /= p;
        i.perspective(e, r).update(),
        u = canvasToBlobUrl(i),
        o ? window.open(u) : a.src = u
    }
    ,
    n.src = a.src
}
!function(t) {
    "use strict";
    t.L.Toolbar2 = (L.Layer || L.Class).extend({
        statics: {
            baseClass: "leaflet-toolbar"
        },
        options: {
            className: "",
            filter: function() {
                return !0
            },
            actions: []
        },
        initialize: function(t) {
            L.setOptions(this, t),
            this._toolbar_type = this.constructor._toolbar_class_id
        },
        addTo: function(t) {
            return this._arguments = [].slice.call(arguments),
            t.addLayer(this),
            this
        },
        onAdd: function(t) {
            var e = t._toolbars[this._toolbar_type];
            0 === this._calculateDepth() && (e && t.removeLayer(e),
            t._toolbars[this._toolbar_type] = this)
        },
        onRemove: function(t) {
            0 === this._calculateDepth() && delete t._toolbars[this._toolbar_type]
        },
        appendToContainer: function(t) {
            var e, r, o, i, a = this.constructor.baseClass + "-" + this._calculateDepth() + " " + this.options.className;
            for (this._container = t,
            this._ul = L.DomUtil.create("ul", a, t),
            this._disabledEvents = ["click", "mousemove", "dblclick", "mousedown", "mouseup", "touchstart"],
            r = 0,
            i = this._disabledEvents.length; r < i; r++)
                L.DomEvent.on(this._ul, this._disabledEvents[r], L.DomEvent.stopPropagation);
            for (e = 0,
            o = this.options.actions.length; e < o; e++)
                (new (this._getActionConstructor(this.options.actions[e])))._createIcon(this, this._ul, this._arguments)
        },
        _getActionConstructor: function(t) {
            var e = this._arguments
              , r = this;
            return t.extend({
                initialize: function() {
                    t.prototype.initialize.apply(this, e)
                },
                enable: function(e) {
                    r._active && r._active.disable(),
                    r._active = this,
                    t.prototype.enable.call(this, e)
                }
            })
        },
        _hide: function() {
            this._ul.style.display = "none"
        },
        _show: function() {
            this._ul.style.display = "block"
        },
        _calculateDepth: function() {
            for (var t = 0, e = this.parentToolbar; e; )
                t += 1,
                e = e.parentToolbar;
            return t
        }
    }),
    L.Evented || L.Toolbar2.include(L.Mixin.Events),
    L.toolbar = {};
    var e = 0;
    L.Toolbar2.extend = function(t) {
        var r = L.extend({}, t.statics, {
            _toolbar_class_id: e
        });
        return e += 1,
        L.extend(t, {
            statics: r
        }),
        L.Class.extend.call(this, t)
    }
    ,
    L.Map.addInitHook((function() {
        this._toolbars = {}
    }
    )),
    L.Toolbar2.Action = L.Handler.extend({
        statics: {
            baseClass: "leaflet-toolbar-icon"
        },
        options: {
            toolbarIcon: {
                html: "",
                className: "",
                tooltip: ""
            },
            subToolbar: new L.Toolbar2
        },
        initialize: function(t) {
            var e = L.Toolbar2.Action.prototype.options.toolbarIcon;
            L.setOptions(this, t),
            this.options.toolbarIcon = L.extend({}, e, this.options.toolbarIcon)
        },
        enable: function(t) {
            t && L.DomEvent.preventDefault(t),
            this._enabled || (this._enabled = !0,
            this.addHooks && this.addHooks())
        },
        disable: function() {
            this._enabled && (this._enabled = !1,
            this.removeHooks && this.removeHooks())
        },
        _createIcon: function(t, e, r) {
            var o = this.options.toolbarIcon;
            this.toolbar = t,
            this._icon = L.DomUtil.create("li", "", e),
            this._link = L.DomUtil.create("a", "", this._icon),
            this._link.innerHTML = o.html,
            this._link.setAttribute("href", "#"),
            this._link.setAttribute("title", o.tooltip),
            L.DomUtil.addClass(this._link, this.constructor.baseClass),
            o.className && L.DomUtil.addClass(this._link, o.className),
            L.DomEvent.on(this._link, "click", this.enable, this),
            this._addSubToolbar(t, this._icon, r)
        },
        _addSubToolbar: function(t, e, r) {
            var o = this.options.subToolbar
              , i = this.addHooks
              , a = this.removeHooks;
            o.parentToolbar = t,
            0 < o.options.actions.length && ((r = [].slice.call(r)).push(this),
            o.addTo.apply(o, r),
            o.appendToContainer(e),
            this.addHooks = function(t) {
                "function" == typeof i && i.call(this, t),
                o._show()
            }
            ,
            this.removeHooks = function(t) {
                "function" == typeof a && a.call(this, t),
                o._hide()
            }
            )
        }
    }),
    L.toolbarAction = function(t) {
        return new L.Toolbar2.Action(t)
    }
    ,
    L.Toolbar2.Action.extendOptions = function(t) {
        return this.extend({
            options: t
        })
    }
    ,
    L.Toolbar2.Control = L.Toolbar2.extend({
        statics: {
            baseClass: "leaflet-control-toolbar " + L.Toolbar2.baseClass
        },
        initialize: function(t) {
            L.Toolbar2.prototype.initialize.call(this, t),
            this._control = new L.Control.Toolbar(this.options)
        },
        onAdd: function(t) {
            this._control.addTo(t),
            L.Toolbar2.prototype.onAdd.call(this, t),
            this.appendToContainer(this._control.getContainer())
        },
        onRemove: function(t) {
            L.Toolbar2.prototype.onRemove.call(this, t),
            this._control.remove ? this._control.remove() : this._control.removeFrom(t)
        }
    }),
    L.Control.Toolbar = L.Control.extend({
        onAdd: function() {
            return L.DomUtil.create("div", "")
        }
    }),
    L.toolbar.control = function(t) {
        return new L.Toolbar2.Control(t)
    }
    ,
    L.Toolbar2.Popup = L.Toolbar2.extend({
        statics: {
            baseClass: "leaflet-popup-toolbar " + L.Toolbar2.baseClass
        },
        options: {
            anchor: [0, 0]
        },
        initialize: function(t, e) {
            L.Toolbar2.prototype.initialize.call(this, e),
            this._marker = new L.Marker(t,{
                icon: new L.DivIcon({
                    className: this.options.className,
                    iconAnchor: [0, 0]
                })
            })
        },
        onAdd: function(t) {
            this._map = t,
            this._marker.addTo(t),
            L.Toolbar2.prototype.onAdd.call(this, t),
            this.appendToContainer(this._marker._icon),
            this._setStyles()
        },
        onRemove: function(t) {
            t.removeLayer(this._marker),
            L.Toolbar2.prototype.onRemove.call(this, t),
            delete this._map
        },
        setLatLng: function(t) {
            return this._marker.setLatLng(t),
            this
        },
        _setStyles: function() {
            for (var t, e, r = this._container, o = this._ul, i = L.point(this.options.anchor), a = o.querySelectorAll(".leaflet-toolbar-icon"), n = [], l = 0, s = 0, c = a.length; s < c; s++)
                a[s].parentNode.parentNode === o && (n.push(parseInt(L.DomUtil.getStyle(a[s], "height"), 10)),
                l = (l += Math.ceil(parseFloat(L.DomUtil.getStyle(a[s], "width")))) + Math.ceil(parseFloat(L.DomUtil.getStyle(a[s], "border-right-width"))));
            o.style.width = l + "px",
            this._tipContainer = L.DomUtil.create("div", "leaflet-toolbar-tip-container", r),
            this._tipContainer.style.width = l + Math.ceil(parseFloat(L.DomUtil.getStyle(o, "border-left-width"))) + "px",
            this._tip = L.DomUtil.create("div", "leaflet-toolbar-tip", this._tipContainer),
            e = Math.max.apply(void 0, n),
            o.style.height = e + "px",
            t = parseInt(L.DomUtil.getStyle(this._tip, "width"), 10),
            e = new L.Point(l / 2,e + 1.414 * t),
            r.style.marginLeft = i.x - e.x + "px",
            r.style.marginTop = i.y - e.y + "px"
        }
    }),
    L.toolbar.popup = function(t) {
        return new L.Toolbar2.Popup(t)
    }
}(window, document);
var fx = function() {
    function t(t, e, r) {
        return Math.max(t, Math.min(e, r))
    }
    function e(t) {
        return {
            _: t,
            loadContentsOf: function(t) {
                N = this._.gl,
                this._.loadContentsOf(t)
            },
            destroy: function() {
                N = this._.gl,
                this._.destroy()
            }
        }
    }
    function r(t) {
        return e(H.fromElement(t))
    }
    function o(t, e, r) {
        return this._.isInitialized && t._.width == this.width && t._.height == this.height || function(t, e) {
            var r = N.UNSIGNED_BYTE;
            if (N.getExtension("OES_texture_float") && N.getExtension("OES_texture_float_linear")) {
                var o = new H(100,100,N.RGBA,N.FLOAT);
                try {
                    o.drawTo((function() {
                        r = N.FLOAT
                    }
                    ))
                } catch (t) {}
                o.destroy()
            }
            this._.texture && this._.texture.destroy(),
            this._.spareTexture && this._.spareTexture.destroy(),
            this.width = t,
            this.height = e,
            this._.texture = new H(t,e,N.RGBA,r),
            this._.spareTexture = new H(t,e,N.RGBA,r),
            this._.extraTexture = this._.extraTexture || new H(0,0,N.RGBA,r),
            this._.flippedShader = this._.flippedShader || new j(null,"uniform sampler2D texture;varying vec2 texCoord;void main(){gl_FragColor=texture2D(texture,vec2(texCoord.x,1.0-texCoord.y));}"),
            this._.isInitialized = !0
        }
        .call(this, e || t._.width, r || t._.height),
        t._.use(),
        this._.texture.drawTo((function() {
            j.getDefaultShader().drawRect()
        }
        )),
        this
    }
    function i() {
        return this._.texture.use(),
        this._.flippedShader.drawRect(),
        this
    }
    function a(t, e, r, o) {
        (r || this._.texture).use(),
        this._.spareTexture.drawTo((function() {
            t.uniforms(e).drawRect()
        }
        )),
        this._.spareTexture.swapWith(o || this._.texture)
    }
    function n(t) {
        return t.parentNode.insertBefore(this, t),
        t.parentNode.removeChild(t),
        this
    }
    function l() {
        var t = new H(this._.texture.width,this._.texture.height,N.RGBA,N.UNSIGNED_BYTE);
        return this._.texture.use(),
        t.drawTo((function() {
            j.getDefaultShader().drawRect()
        }
        )),
        e(t)
    }
    function s() {
        var t = this._.texture.width
          , e = this._.texture.height
          , r = new Uint8Array(4 * t * e);
        return this._.texture.drawTo((function() {
            N.readPixels(0, 0, t, e, N.RGBA, N.UNSIGNED_BYTE, r)
        }
        )),
        r
    }
    function c(t) {
        return function() {
            return N = this._.gl,
            t.apply(this, arguments)
        }
    }
    function u(t, e, r, o, i, a, n, l) {
        var s = r - i
          , c = o - a
          , u = n - i
          , h = l - a
          , f = s * h - u * c;
        return [r - t + (u = ((i = t - r + i - n) * h - u * (a = e - o + a - l)) / f) * r, o - e + u * o, u, n - t + (s = (s * a - i * c) / f) * n, l - e + s * l, s, t, e, 1]
    }
    function h(t) {
        var e = t[0]
          , r = t[1]
          , o = t[2]
          , i = t[3]
          , a = t[4]
          , n = t[5]
          , l = t[6]
          , s = t[7]
          , c = e * a * (t = t[8]) - e * n * s - r * i * t + r * n * l + o * i * s - o * a * l;
        return [(a * t - n * s) / c, (o * s - r * t) / c, (r * n - o * a) / c, (n * l - i * t) / c, (e * t - o * l) / c, (o * i - e * n) / c, (i * s - a * l) / c, (r * l - e * s) / c, (e * a - r * i) / c]
    }
    function f(t) {
        var e = t.length;
        this.xa = [],
        this.ya = [],
        this.u = [],
        this.y2 = [],
        t.sort((function(t, e) {
            return t[0] - e[0]
        }
        ));
        for (var r = 0; r < e; r++)
            this.xa.push(t[r][0]),
            this.ya.push(t[r][1]);
        for (this.u[0] = 0,
        this.y2[0] = 0,
        r = 1; r < e - 1; ++r) {
            t = this.xa[r + 1] - this.xa[r - 1];
            var o = (this.xa[r] - this.xa[r - 1]) / t
              , i = o * this.y2[r - 1] + 2;
            this.y2[r] = (o - 1) / i,
            this.u[r] = (6 * ((this.ya[r + 1] - this.ya[r]) / (this.xa[r + 1] - this.xa[r]) - (this.ya[r] - this.ya[r - 1]) / (this.xa[r] - this.xa[r - 1])) / t - o * this.u[r - 1]) / i
        }
        for (this.y2[e - 1] = 0,
        r = e - 2; 0 <= r; --r)
            this.y2[r] = this.y2[r] * this.y2[r + 1] + this.u[r]
    }
    function d(t, e) {
        return new j(null,t + "uniform sampler2D texture;uniform vec2 texSize;varying vec2 texCoord;void main(){vec2 coord=texCoord*texSize;" + e + "gl_FragColor=texture2D(texture,coord/texSize);vec2 clampedCoord=clamp(coord,vec2(0.0),texSize);if(coord!=clampedCoord){gl_FragColor.a*=max(0.0,1.0-length(coord-clampedCoord));}}")
    }
    function m(e) {
        return N.noise = N.noise || new j(null,"uniform sampler2D texture;uniform float amount;varying vec2 texCoord;float rand(vec2 co){return fract(sin(dot(co.xy,vec2(12.9898,78.233)))*43758.5453);}void main(){vec4 color=texture2D(texture,texCoord);float diff=(rand(texCoord)-0.5)*amount;color.r+=diff;color.g+=diff;color.b+=diff;gl_FragColor=color;}"),
        a.call(this, N.noise, {
            amount: t(0, e, 1)
        }),
        this
    }
    function g(e) {
        return N.vibrance = N.vibrance || new j(null,"uniform sampler2D texture;uniform float amount;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);float average=(color.r+color.g+color.b)/3.0;float mx=max(color.r,max(color.g,color.b));float amt=(mx-average)*(-amount*3.0);color.rgb=mix(color.rgb,vec3(mx),amt);gl_FragColor=color;}"),
        a.call(this, N.vibrance, {
            amount: t(-1, e, 1)
        }),
        this
    }
    function p(e, r) {
        return N.vignette = N.vignette || new j(null,"uniform sampler2D texture;uniform float size;uniform float amount;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);float dist=distance(texCoord,vec2(0.5,0.5));color.rgb*=smoothstep(0.8,size*0.799,dist*(amount+size));gl_FragColor=color;}"),
        a.call(this, N.vignette, {
            size: t(0, e, 1),
            amount: t(0, r, 1)
        }),
        this
    }
    function x(t) {
        N.denoise = N.denoise || new j(null,"uniform sampler2D texture;uniform float exponent;uniform float strength;uniform vec2 texSize;varying vec2 texCoord;void main(){vec4 center=texture2D(texture,texCoord);vec4 color=vec4(0.0);float total=0.0;for(float x=-4.0;x<=4.0;x+=1.0){for(float y=-4.0;y<=4.0;y+=1.0){vec4 sample=texture2D(texture,texCoord+vec2(x,y)/texSize);float weight=1.0-abs(dot(sample.rgb-center.rgb,vec3(0.25)));weight=pow(weight,exponent);color+=sample*weight;total+=weight;}}gl_FragColor=color/total;}");
        for (var e = 0; e < 2; e++)
            a.call(this, N.denoise, {
                exponent: Math.max(0, t),
                texSize: [this.width, this.height]
            });
        return this
    }
    function v(e, r) {
        return N.brightnessContrast = N.brightnessContrast || new j(null,"uniform sampler2D texture;uniform float brightness;uniform float contrast;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);color.rgb+=brightness;if(contrast>0.0){color.rgb=(color.rgb-0.5)/(1.0-contrast)+0.5;}else{color.rgb=(color.rgb-0.5)*(1.0+contrast)+0.5;}gl_FragColor=color;}"),
        a.call(this, N.brightnessContrast, {
            brightness: t(-1, e, 1),
            contrast: t(-1, r, 1)
        }),
        this
    }
    function b(e) {
        e = new f(e);
        for (var r = [], o = 0; o < 256; o++)
            r.push(t(0, Math.floor(256 * e.interpolate(o / 255)), 255));
        return r
    }
    function y(t, e, r) {
        t = b(t),
        1 == arguments.length ? e = r = t : (e = b(e),
        r = b(r));
        for (var o = [], i = 0; i < 256; i++)
            o.splice(o.length, 0, t[i], e[i], r[i], 255);
        return this._.extraTexture.initFromBytes(256, 1, o),
        this._.extraTexture.use(1),
        N.curves = N.curves || new j(null,"uniform sampler2D texture;uniform sampler2D map;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);color.r=texture2D(map,vec2(color.r)).r;color.g=texture2D(map,vec2(color.g)).g;color.b=texture2D(map,vec2(color.b)).b;gl_FragColor=color;}"),
        N.curves.textures({
            map: 1
        }),
        a.call(this, N.curves, {}),
        this
    }
    function _(t, e) {
        return N.unsharpMask = N.unsharpMask || new j(null,"uniform sampler2D blurredTexture;uniform sampler2D originalTexture;uniform float strength;uniform float threshold;varying vec2 texCoord;void main(){vec4 blurred=texture2D(blurredTexture,texCoord);vec4 original=texture2D(originalTexture,texCoord);gl_FragColor=mix(blurred,original,1.0+strength);}"),
        this._.extraTexture.ensureFormat(this._.texture),
        this._.texture.use(),
        this._.extraTexture.drawTo((function() {
            j.getDefaultShader().drawRect()
        }
        )),
        this._.extraTexture.use(1),
        this.triangleBlur(t),
        N.unsharpMask.textures({
            originalTexture: 1
        }),
        a.call(this, N.unsharpMask, {
            strength: e
        }),
        this._.extraTexture.unuse(1),
        this
    }
    function T(e) {
        return N.sepia = N.sepia || new j(null,"uniform sampler2D texture;uniform float amount;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);float r=color.r;float g=color.g;float b=color.b;color.r=min(1.0,(r*(1.0-(0.607*amount)))+(g*(0.769*amount))+(b*(0.189*amount)));color.g=min(1.0,(r*0.349*amount)+(g*(1.0-(0.314*amount)))+(b*0.168*amount));color.b=min(1.0,(r*0.272*amount)+(g*0.534*amount)+(b*(1.0-(0.869*amount))));gl_FragColor=color;}"),
        a.call(this, N.sepia, {
            amount: t(0, e, 1)
        }),
        this
    }
    function w(e, r) {
        return N.hueSaturation = N.hueSaturation || new j(null,"uniform sampler2D texture;uniform float hue;uniform float saturation;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);float angle=hue*3.14159265;float s=sin(angle),c=cos(angle);vec3 weights=(vec3(2.0*c,-sqrt(3.0)*s-c,sqrt(3.0)*s-c)+1.0)/3.0;float len=length(color.rgb);color.rgb=vec3(dot(color.rgb,weights.xyz),dot(color.rgb,weights.zxy),dot(color.rgb,weights.yzx));float average=(color.r+color.g+color.b)/3.0;if(saturation>0.0){color.rgb+=(average-color.rgb)*(1.0-1.0/(1.001-saturation));}else{color.rgb+=(average-color.rgb)*(-saturation);}gl_FragColor=color;}"),
        a.call(this, N.hueSaturation, {
            hue: t(-1, e, 1),
            saturation: t(-1, r, 1)
        }),
        this
    }
    function S(t, e, r) {
        return N.zoomBlur = N.zoomBlur || new j(null,"uniform sampler2D texture;uniform vec2 center;uniform float strength;uniform vec2 texSize;varying vec2 texCoord;" + q + "void main(){vec4 color=vec4(0.0);float total=0.0;vec2 toCenter=center-texCoord*texSize;float offset=random(vec3(12.9898,78.233,151.7182),0.0);for(float t=0.0;t<=40.0;t++){float percent=(t+offset)/40.0;float weight=4.0*(percent-percent*percent);vec4 sample=texture2D(texture,texCoord+toCenter*percent*strength/texSize);sample.rgb*=sample.a;color+=sample*weight;total+=weight;}gl_FragColor=color/total;gl_FragColor.rgb/=gl_FragColor.a+0.00001;}"),
        a.call(this, N.zoomBlur, {
            center: [t, e],
            strength: r,
            texSize: [this.width, this.height]
        }),
        this
    }
    function C(t, e, r, o, i, n) {
        N.tiltShift = N.tiltShift || new j(null,"uniform sampler2D texture;uniform float blurRadius;uniform float gradientRadius;uniform vec2 start;uniform vec2 end;uniform vec2 delta;uniform vec2 texSize;varying vec2 texCoord;" + q + "void main(){vec4 color=vec4(0.0);float total=0.0;float offset=random(vec3(12.9898,78.233,151.7182),0.0);vec2 normal=normalize(vec2(start.y-end.y,end.x-start.x));float radius=smoothstep(0.0,1.0,abs(dot(texCoord*texSize-start,normal))/gradientRadius)*blurRadius;for(float t=-30.0;t<=30.0;t++){float percent=(t+offset-0.5)/30.0;float weight=1.0-abs(percent);vec4 sample=texture2D(texture,texCoord+delta/texSize*percent*radius);sample.rgb*=sample.a;color+=sample*weight;total+=weight;}gl_FragColor=color/total;gl_FragColor.rgb/=gl_FragColor.a+0.00001;}");
        var l = r - t
          , s = o - e
          , c = Math.sqrt(l * l + s * s);
        return a.call(this, N.tiltShift, {
            blurRadius: i,
            gradientRadius: n,
            start: [t, e],
            end: [r, o],
            delta: [l / c, s / c],
            texSize: [this.width, this.height]
        }),
        a.call(this, N.tiltShift, {
            blurRadius: i,
            gradientRadius: n,
            start: [t, e],
            end: [r, o],
            delta: [-s / c, l / c],
            texSize: [this.width, this.height]
        }),
        this
    }
    function E(e, r, o) {
        N.lensBlurPrePass = N.lensBlurPrePass || new j(null,"uniform sampler2D texture;uniform float power;varying vec2 texCoord;void main(){vec4 color=texture2D(texture,texCoord);color=pow(color,vec4(power));gl_FragColor=vec4(color);}");
        var i = "uniform sampler2D texture0;uniform sampler2D texture1;uniform vec2 delta0;uniform vec2 delta1;uniform float power;varying vec2 texCoord;" + q + "vec4 sample(vec2 delta){float offset=random(vec3(delta,151.7182),0.0);vec4 color=vec4(0.0);float total=0.0;for(float t=0.0;t<=30.0;t++){float percent=(t+offset)/30.0;color+=texture2D(texture0,texCoord+delta*percent);total+=1.0;}return color/total;}";
        N.lensBlur0 = N.lensBlur0 || new j(null,i + "void main(){gl_FragColor=sample(delta0);}"),
        N.lensBlur1 = N.lensBlur1 || new j(null,i + "void main(){gl_FragColor=(sample(delta0)+sample(delta1))*0.5;}"),
        N.lensBlur2 = N.lensBlur2 || new j(null,i + "void main(){vec4 color=(sample(delta0)+2.0*texture2D(texture1,texCoord))/3.0;gl_FragColor=pow(color,vec4(power));}").textures({
            texture1: 1
        }),
        i = [];
        for (var n = 0; n < 3; n++) {
            var l = o + 2 * n * Math.PI / 3;
            i.push([e * Math.sin(l) / this.width, e * Math.cos(l) / this.height])
        }
        return e = Math.pow(10, t(-1, r, 1)),
        a.call(this, N.lensBlurPrePass, {
            power: e
        }),
        this._.extraTexture.ensureFormat(this._.texture),
        a.call(this, N.lensBlur0, {
            delta0: i[0]
        }, this._.texture, this._.extraTexture),
        a.call(this, N.lensBlur1, {
            delta0: i[1],
            delta1: i[2]
        }, this._.extraTexture, this._.extraTexture),
        a.call(this, N.lensBlur0, {
            delta0: i[1]
        }),
        this._.extraTexture.use(1),
        a.call(this, N.lensBlur2, {
            power: 1 / e,
            delta0: i[2]
        }),
        this
    }
    function D(t) {
        return N.triangleBlur = N.triangleBlur || new j(null,"uniform sampler2D texture;uniform vec2 delta;varying vec2 texCoord;" + q + "void main(){vec4 color=vec4(0.0);float total=0.0;float offset=random(vec3(12.9898,78.233,151.7182),0.0);for(float t=-30.0;t<=30.0;t++){float percent=(t+offset-0.5)/30.0;float weight=1.0-abs(percent);vec4 sample=texture2D(texture,texCoord+delta*percent);sample.rgb*=sample.a;color+=sample*weight;total+=weight;}gl_FragColor=color/total;gl_FragColor.rgb/=gl_FragColor.a+0.00001;}"),
        a.call(this, N.triangleBlur, {
            delta: [t / this.width, 0]
        }),
        a.call(this, N.triangleBlur, {
            delta: [0, t / this.height]
        }),
        this
    }
    function R(t) {
        return N.edgeWork1 = N.edgeWork1 || new j(null,"uniform sampler2D texture;uniform vec2 delta;varying vec2 texCoord;" + q + "void main(){vec2 color=vec2(0.0);vec2 total=vec2(0.0);float offset=random(vec3(12.9898,78.233,151.7182),0.0);for(float t=-30.0;t<=30.0;t++){float percent=(t+offset-0.5)/30.0;float weight=1.0-abs(percent);vec3 sample=texture2D(texture,texCoord+delta*percent).rgb;float average=(sample.r+sample.g+sample.b)/3.0;color.x+=average*weight;total.x+=weight;if(abs(t)<15.0){weight=weight*2.0-1.0;color.y+=average*weight;total.y+=weight;}}gl_FragColor=vec4(color/total,0.0,1.0);}"),
        N.edgeWork2 = N.edgeWork2 || new j(null,"uniform sampler2D texture;uniform vec2 delta;varying vec2 texCoord;" + q + "void main(){vec2 color=vec2(0.0);vec2 total=vec2(0.0);float offset=random(vec3(12.9898,78.233,151.7182),0.0);for(float t=-30.0;t<=30.0;t++){float percent=(t+offset-0.5)/30.0;float weight=1.0-abs(percent);vec2 sample=texture2D(texture,texCoord+delta*percent).xy;color.x+=sample.x*weight;total.x+=weight;if(abs(t)<15.0){weight=weight*2.0-1.0;color.y+=sample.y*weight;total.y+=weight;}}float c=clamp(10000.0*(color.y/total.y-color.x/total.x)+0.5,0.0,1.0);gl_FragColor=vec4(c,c,c,1.0);}"),
        a.call(this, N.edgeWork1, {
            delta: [t / this.width, 0]
        }),
        a.call(this, N.edgeWork2, {
            delta: [0, t / this.height]
        }),
        this
    }
    function F(t, e, r) {
        return N.hexagonalPixelate = N.hexagonalPixelate || new j(null,"uniform sampler2D texture;uniform vec2 center;uniform float scale;uniform vec2 texSize;varying vec2 texCoord;void main(){vec2 tex=(texCoord*texSize-center)/scale;tex.y/=0.866025404;tex.x-=tex.y*0.5;vec2 a;if(tex.x+tex.y-floor(tex.x)-floor(tex.y)<1.0)a=vec2(floor(tex.x),floor(tex.y));else a=vec2(ceil(tex.x),ceil(tex.y));vec2 b=vec2(ceil(tex.x),floor(tex.y));vec2 c=vec2(floor(tex.x),ceil(tex.y));vec3 TEX=vec3(tex.x,tex.y,1.0-tex.x-tex.y);vec3 A=vec3(a.x,a.y,1.0-a.x-a.y);vec3 B=vec3(b.x,b.y,1.0-b.x-b.y);vec3 C=vec3(c.x,c.y,1.0-c.x-c.y);float alen=length(TEX-A);float blen=length(TEX-B);float clen=length(TEX-C);vec2 choice;if(alen<blen){if(alen<clen)choice=a;else choice=c;}else{if(blen<clen)choice=b;else choice=c;}choice.x+=choice.y*0.5;choice.y*=0.866025404;choice*=scale/texSize;gl_FragColor=texture2D(texture,choice+center/texSize);}"),
        a.call(this, N.hexagonalPixelate, {
            center: [t, e],
            scale: r,
            texSize: [this.width, this.height]
        }),
        this
    }
    function A(t, e, r, o) {
        return N.colorHalftone = N.colorHalftone || new j(null,"uniform sampler2D texture;uniform vec2 center;uniform float angle;uniform float scale;uniform vec2 texSize;varying vec2 texCoord;float pattern(float angle){float s=sin(angle),c=cos(angle);vec2 tex=texCoord*texSize-center;vec2 point=vec2(c*tex.x-s*tex.y,s*tex.x+c*tex.y)*scale;return(sin(point.x)*sin(point.y))*4.0;}void main(){vec4 color=texture2D(texture,texCoord);vec3 cmy=1.0-color.rgb;float k=min(cmy.x,min(cmy.y,cmy.z));cmy=(cmy-k)/(1.0-k);cmy=clamp(cmy*10.0-3.0+vec3(pattern(angle+0.26179),pattern(angle+1.30899),pattern(angle)),0.0,1.0);k=clamp(k*10.0-5.0+pattern(angle+0.78539),0.0,1.0);gl_FragColor=vec4(1.0-cmy-k,color.a);}"),
        a.call(this, N.colorHalftone, {
            center: [t, e],
            angle: r,
            scale: Math.PI / o,
            texSize: [this.width, this.height]
        }),
        this
    }
    function P(t) {
        return N.ink = N.ink || new j(null,"uniform sampler2D texture;uniform float strength;uniform vec2 texSize;varying vec2 texCoord;void main(){vec2 dx=vec2(1.0/texSize.x,0.0);vec2 dy=vec2(0.0,1.0/texSize.y);vec4 color=texture2D(texture,texCoord);float bigTotal=0.0;float smallTotal=0.0;vec3 bigAverage=vec3(0.0);vec3 smallAverage=vec3(0.0);for(float x=-2.0;x<=2.0;x+=1.0){for(float y=-2.0;y<=2.0;y+=1.0){vec3 sample=texture2D(texture,texCoord+dx*x+dy*y).rgb;bigAverage+=sample;bigTotal+=1.0;if(abs(x)+abs(y)<2.0){smallAverage+=sample;smallTotal+=1.0;}}}vec3 edge=max(vec3(0.0),bigAverage/bigTotal-smallAverage/smallTotal);gl_FragColor=vec4(color.rgb-dot(edge,edge)*strength*100000.0,color.a);}"),
        a.call(this, N.ink, {
            strength: t * t * t * t * t,
            texSize: [this.width, this.height]
        }),
        this
    }
    function U(t, e, r, o) {
        return N.dotScreen = N.dotScreen || new j(null,"uniform sampler2D texture;uniform vec2 center;uniform float angle;uniform float scale;uniform vec2 texSize;varying vec2 texCoord;float pattern(){float s=sin(angle),c=cos(angle);vec2 tex=texCoord*texSize-center;vec2 point=vec2(c*tex.x-s*tex.y,s*tex.x+c*tex.y)*scale;return(sin(point.x)*sin(point.y))*4.0;}void main(){vec4 color=texture2D(texture,texCoord);float average=(color.r+color.g+color.b)/3.0;gl_FragColor=vec4(vec3(average*10.0-5.0+pattern()),color.a);}"),
        a.call(this, N.dotScreen, {
            center: [t, e],
            angle: r,
            scale: Math.PI / o,
            texSize: [this.width, this.height]
        }),
        this
    }
    function L(t, e, r) {
        if (N.matrixWarp = N.matrixWarp || d("uniform mat3 matrix;uniform bool useTextureSpace;", "if(useTextureSpace)coord=coord/texSize*2.0-1.0;vec3 warp=matrix*vec3(coord,1.0);coord=warp.xy/warp.z;if(useTextureSpace)coord=(coord*0.5+0.5)*texSize;"),
        4 == (t = Array.prototype.concat.apply([], t)).length)
            t = [t[0], t[1], 0, t[2], t[3], 0, 0, 0, 1];
        else if (9 != t.length)
            throw "can only warp with 2x2 or 3x3 matrix";
        return a.call(this, N.matrixWarp, {
            matrix: e ? h(t) : t,
            texSize: [this.width, this.height],
            useTextureSpace: 0 | r
        }),
        this
    }
    function I(t, e, r, o) {
        return N.swirl = N.swirl || d("uniform float radius;uniform float angle;uniform vec2 center;", "coord-=center;float distance=length(coord);if(distance<radius){float percent=(radius-distance)/radius;float theta=percent*percent*angle;float s=sin(theta);float c=cos(theta);coord=vec2(coord.x*c-coord.y*s,coord.x*s+coord.y*c);}coord+=center;"),
        a.call(this, N.swirl, {
            radius: r,
            center: [t, e],
            angle: o,
            texSize: [this.width, this.height]
        }),
        this
    }
    function B(e, r, o, i) {
        return N.bulgePinch = N.bulgePinch || d("uniform float radius;uniform float strength;uniform vec2 center;", "coord-=center;float distance=length(coord);if(distance<radius){float percent=distance/radius;if(strength>0.0){coord*=mix(1.0,smoothstep(0.0,radius/distance,percent),strength*0.75);}else{coord*=mix(1.0,pow(percent,1.0+strength*0.75)*radius/distance,1.0-percent);}}coord+=center;"),
        a.call(this, N.bulgePinch, {
            radius: o,
            strength: t(-1, i, 1),
            center: [e, r],
            texSize: [this.width, this.height]
        }),
        this
    }
    function G(t, e) {
        return e = u.apply(null, e),
        t = u.apply(null, t),
        e = h(e),
        this.matrixWarp([e[0] * t[0] + e[1] * t[3] + e[2] * t[6], e[0] * t[1] + e[1] * t[4] + e[2] * t[7], e[0] * t[2] + e[1] * t[5] + e[2] * t[8], e[3] * t[0] + e[4] * t[3] + e[5] * t[6], e[3] * t[1] + e[4] * t[4] + e[5] * t[7], e[3] * t[2] + e[4] * t[5] + e[5] * t[8], e[6] * t[0] + e[7] * t[3] + e[8] * t[6], e[6] * t[1] + e[7] * t[4] + e[8] * t[7], e[6] * t[2] + e[7] * t[5] + e[8] * t[8]])
    }
    var M, k, N, O = {};
    function X() {}
    try {
        var z = document.createElement("canvas").getContext("experimental-webgl")
    } catch (O) {}
    z && -1 === z.getSupportedExtensions().indexOf("OES_texture_float_linear") && function(t) {
        var e, r, o, i;
        if (t.getExtension("OES_texture_float"))
            return e = t.createFramebuffer(),
            r = t.createTexture(),
            t.bindTexture(t.TEXTURE_2D, r),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_MAG_FILTER, t.NEAREST),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_MIN_FILTER, t.NEAREST),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_WRAP_S, t.CLAMP_TO_EDGE),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_WRAP_T, t.CLAMP_TO_EDGE),
            t.texImage2D(t.TEXTURE_2D, 0, t.RGBA, 1, 1, 0, t.RGBA, t.UNSIGNED_BYTE, null),
            t.bindFramebuffer(t.FRAMEBUFFER, e),
            t.framebufferTexture2D(t.FRAMEBUFFER, t.COLOR_ATTACHMENT0, t.TEXTURE_2D, r, 0),
            e = t.createTexture(),
            t.bindTexture(t.TEXTURE_2D, e),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_MAG_FILTER, t.LINEAR),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_MIN_FILTER, t.LINEAR),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_WRAP_S, t.CLAMP_TO_EDGE),
            t.texParameteri(t.TEXTURE_2D, t.TEXTURE_WRAP_T, t.CLAMP_TO_EDGE),
            t.texImage2D(t.TEXTURE_2D, 0, t.RGBA, 2, 2, 0, t.RGBA, t.FLOAT, new Float32Array([2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])),
            r = t.createProgram(),
            o = t.createShader(t.VERTEX_SHADER),
            i = t.createShader(t.FRAGMENT_SHADER),
            t.shaderSource(o, "attribute vec2 vertex;void main(){gl_Position=vec4(vertex,0.0,1.0);}"),
            t.shaderSource(i, "uniform sampler2D texture;void main(){gl_FragColor=texture2D(texture,vec2(0.5));}"),
            t.compileShader(o),
            t.compileShader(i),
            t.attachShader(r, o),
            t.attachShader(r, i),
            t.linkProgram(r),
            o = t.createBuffer(),
            t.bindBuffer(t.ARRAY_BUFFER, o),
            t.bufferData(t.ARRAY_BUFFER, new Float32Array([0, 0]), t.STREAM_DRAW),
            t.enableVertexAttribArray(0),
            t.vertexAttribPointer(0, 2, t.FLOAT, !1, 0, 0),
            o = new Uint8Array(4),
            t.useProgram(r),
            t.viewport(0, 0, 1, 1),
            t.bindTexture(t.TEXTURE_2D, e),
            t.drawArrays(t.POINTS, 0, 1),
            t.readPixels(0, 0, 1, 1, t.RGBA, t.UNSIGNED_BYTE, o),
            127 === o[0] || 128 === o[0]
    }(z) && (M = WebGLRenderingContext.prototype.getExtension,
    k = WebGLRenderingContext.prototype.getSupportedExtensions,
    WebGLRenderingContext.prototype.getExtension = function(t) {
        return "OES_texture_float_linear" === t ? (void 0 === this.$OES_texture_float_linear$ && Object.defineProperty(this, "$OES_texture_float_linear$", {
            enumerable: !1,
            configurable: !1,
            writable: !1,
            value: new X
        }),
        this.$OES_texture_float_linear$) : M.call(this, t)
    }
    ,
    WebGLRenderingContext.prototype.getSupportedExtensions = function() {
        var t = k.call(this);
        return -1 === t.indexOf("OES_texture_float_linear") && t.push("OES_texture_float_linear"),
        t
    }
    ),
    O.canvas = function() {
        var t = document.createElement("canvas");
        try {
            N = t.getContext("experimental-webgl", {
                premultipliedAlpha: !1
            })
        } catch (t) {
            N = null
        }
        if (N)
            return t._ = {
                gl: N,
                isInitialized: !1,
                texture: null,
                spareTexture: null,
                flippedShader: null
            },
            t.texture = c(r),
            t.draw = c(o),
            t.update = c(i),
            t.replace = c(n),
            t.contents = c(l),
            t.getPixelArray = c(s),
            t.brightnessContrast = c(v),
            t.hexagonalPixelate = c(F),
            t.hueSaturation = c(w),
            t.colorHalftone = c(A),
            t.triangleBlur = c(D),
            t.unsharpMask = c(_),
            t.perspective = c(G),
            t.matrixWarp = c(L),
            t.bulgePinch = c(B),
            t.tiltShift = c(C),
            t.dotScreen = c(U),
            t.edgeWork = c(R),
            t.lensBlur = c(E),
            t.zoomBlur = c(S),
            t.noise = c(m),
            t.denoise = c(x),
            t.curves = c(y),
            t.swirl = c(I),
            t.ink = c(P),
            t.vignette = c(p),
            t.vibrance = c(g),
            t.sepia = c(T),
            t;
        throw "This browser does not support WebGL"
    }
    ,
    O.splineInterpolate = b,
    Y.fromElement = function(t) {
        var e = new Y(0,0,N.RGBA,N.UNSIGNED_BYTE);
        return e.loadContentsOf(t),
        e
    }
    ,
    Y.prototype.loadContentsOf = function(t) {
        this.width = t.width || t.videoWidth,
        this.height = t.height || t.videoHeight,
        N.bindTexture(N.TEXTURE_2D, this.id),
        N.texImage2D(N.TEXTURE_2D, 0, this.format, this.format, this.type, t)
    }
    ,
    Y.prototype.initFromBytes = function(t, e, r) {
        this.width = t,
        this.height = e,
        this.format = N.RGBA,
        this.type = N.UNSIGNED_BYTE,
        N.bindTexture(N.TEXTURE_2D, this.id),
        N.texImage2D(N.TEXTURE_2D, 0, N.RGBA, t, e, 0, N.RGBA, this.type, new Uint8Array(r))
    }
    ,
    Y.prototype.destroy = function() {
        N.deleteTexture(this.id),
        this.id = null
    }
    ,
    Y.prototype.use = function(t) {
        N.activeTexture(N.TEXTURE0 + (t || 0)),
        N.bindTexture(N.TEXTURE_2D, this.id)
    }
    ,
    Y.prototype.unuse = function(t) {
        N.activeTexture(N.TEXTURE0 + (t || 0)),
        N.bindTexture(N.TEXTURE_2D, null)
    }
    ,
    Y.prototype.ensureFormat = function(t, e, r, o) {
        var i;
        1 == arguments.length && (t = (i = arguments[0]).width,
        e = i.height,
        r = i.format,
        o = i.type),
        t == this.width && e == this.height && r == this.format && o == this.type || (this.width = t,
        this.height = e,
        this.format = r,
        this.type = o,
        N.bindTexture(N.TEXTURE_2D, this.id),
        N.texImage2D(N.TEXTURE_2D, 0, this.format, t, e, 0, this.format, this.type, null))
    }
    ,
    Y.prototype.drawTo = function(t) {
        if (N.framebuffer = N.framebuffer || N.createFramebuffer(),
        N.bindFramebuffer(N.FRAMEBUFFER, N.framebuffer),
        N.framebufferTexture2D(N.FRAMEBUFFER, N.COLOR_ATTACHMENT0, N.TEXTURE_2D, this.id, 0),
        N.checkFramebufferStatus(N.FRAMEBUFFER) !== N.FRAMEBUFFER_COMPLETE)
            throw Error("incomplete framebuffer");
        N.viewport(0, 0, this.width, this.height),
        t(),
        N.bindFramebuffer(N.FRAMEBUFFER, null)
    }
    ,
    W = null,
    Y.prototype.fillUsingCanvas = function(t) {
        return t(V(this)),
        this.format = N.RGBA,
        this.type = N.UNSIGNED_BYTE,
        N.bindTexture(N.TEXTURE_2D, this.id),
        N.texImage2D(N.TEXTURE_2D, 0, N.RGBA, N.RGBA, N.UNSIGNED_BYTE, W),
        this
    }
    ,
    Y.prototype.toImage = function(t) {
        this.use(),
        j.getDefaultShader().drawRect();
        var e = 4 * this.width * this.height
          , r = new Uint8Array(e)
          , o = V(this)
          , i = o.createImageData(this.width, this.height);
        N.readPixels(0, 0, this.width, this.height, N.RGBA, N.UNSIGNED_BYTE, r);
        for (var a = 0; a < e; a++)
            i.data[a] = r[a];
        o.putImageData(i, 0, 0),
        t.src = W.toDataURL()
    }
    ,
    Y.prototype.swapWith = function(t) {
        var e = t.id;
        t.id = this.id,
        this.id = e,
        e = t.width,
        t.width = this.width,
        this.width = e,
        e = t.height,
        t.height = this.height,
        this.height = e,
        e = t.format,
        t.format = this.format,
        this.format = e
    }
    ;
    var W, H = Y;
    function Y(t, e, r, o) {
        this.gl = N,
        this.id = N.createTexture(),
        this.width = t,
        this.height = e,
        this.format = r,
        this.type = o,
        N.bindTexture(N.TEXTURE_2D, this.id),
        N.texParameteri(N.TEXTURE_2D, N.TEXTURE_MAG_FILTER, N.LINEAR),
        N.texParameteri(N.TEXTURE_2D, N.TEXTURE_MIN_FILTER, N.LINEAR),
        N.texParameteri(N.TEXTURE_2D, N.TEXTURE_WRAP_S, N.CLAMP_TO_EDGE),
        N.texParameteri(N.TEXTURE_2D, N.TEXTURE_WRAP_T, N.CLAMP_TO_EDGE),
        t && e && N.texImage2D(N.TEXTURE_2D, 0, this.format, t, e, 0, this.format, this.type, null)
    }
    function V(t) {
        return (W = null == W ? document.createElement("canvas") : W).width = t.width,
        W.height = t.height,
        (t = W.getContext("2d")).clearRect(0, 0, W.width, W.height),
        t
    }
    f.prototype.interpolate = function(t) {
        for (var e = 0, r = this.ya.length - 1; 1 < r - e; ) {
            var o = r + e >> 1;
            this.xa[o] > t ? r = o : e = o
        }
        o = this.xa[r] - this.xa[e];
        var i = (this.xa[r] - t) / o;
        return t = (t - this.xa[e]) / o,
        i * this.ya[e] + t * this.ya[r] + ((i * i * i - i) * this.y2[e] + (t * t * t - t) * this.y2[r]) * o * o / 6
    }
    ,
    $.prototype.destroy = function() {
        N.deleteProgram(this.program),
        this.program = null
    }
    ,
    $.prototype.uniforms = function(t) {
        for (var e in N.useProgram(this.program),
        t)
            if (t.hasOwnProperty(e)) {
                var r = N.getUniformLocation(this.program, e);
                if (null !== r) {
                    var o = t[e];
                    if ("[object Array]" == Object.prototype.toString.call(o))
                        switch (o.length) {
                        case 1:
                            N.uniform1fv(r, new Float32Array(o));
                            break;
                        case 2:
                            N.uniform2fv(r, new Float32Array(o));
                            break;
                        case 3:
                            N.uniform3fv(r, new Float32Array(o));
                            break;
                        case 4:
                            N.uniform4fv(r, new Float32Array(o));
                            break;
                        case 9:
                            N.uniformMatrix3fv(r, !1, new Float32Array(o));
                            break;
                        case 16:
                            N.uniformMatrix4fv(r, !1, new Float32Array(o));
                            break;
                        default:
                            throw "dont't know how to load uniform \"" + e + '" of length ' + o.length
                        }
                    else {
                        if ("[object Number]" != Object.prototype.toString.call(o))
                            throw 'attempted to set uniform "' + e + '" to invalid value ' + (o || "undefined").toString();
                        N.uniform1f(r, o)
                    }
                }
            }
        return this
    }
    ,
    $.prototype.textures = function(t) {
        for (var e in N.useProgram(this.program),
        t)
            t.hasOwnProperty(e) && N.uniform1i(N.getUniformLocation(this.program, e), t[e]);
        return this
    }
    ,
    $.prototype.drawRect = function(t, e, r, o) {
        var i = N.getParameter(N.VIEWPORT);
        e = void 0 !== e ? (e - i[1]) / i[3] : 0,
        t = void 0 !== t ? (t - i[0]) / i[2] : 0,
        r = void 0 !== r ? (r - i[0]) / i[2] : 1,
        o = void 0 !== o ? (o - i[1]) / i[3] : 1,
        null == N.vertexBuffer && (N.vertexBuffer = N.createBuffer()),
        N.bindBuffer(N.ARRAY_BUFFER, N.vertexBuffer),
        N.bufferData(N.ARRAY_BUFFER, new Float32Array([t, e, t, o, r, e, r, o]), N.STATIC_DRAW),
        null == N.texCoordBuffer && (N.texCoordBuffer = N.createBuffer(),
        N.bindBuffer(N.ARRAY_BUFFER, N.texCoordBuffer),
        N.bufferData(N.ARRAY_BUFFER, new Float32Array([0, 0, 0, 1, 1, 0, 1, 1]), N.STATIC_DRAW)),
        null == this.vertexAttribute && (this.vertexAttribute = N.getAttribLocation(this.program, "vertex"),
        N.enableVertexAttribArray(this.vertexAttribute)),
        null == this.texCoordAttribute && (this.texCoordAttribute = N.getAttribLocation(this.program, "_texCoord"),
        N.enableVertexAttribArray(this.texCoordAttribute)),
        N.useProgram(this.program),
        N.bindBuffer(N.ARRAY_BUFFER, N.vertexBuffer),
        N.vertexAttribPointer(this.vertexAttribute, 2, N.FLOAT, !1, 0, 0),
        N.bindBuffer(N.ARRAY_BUFFER, N.texCoordBuffer),
        N.vertexAttribPointer(this.texCoordAttribute, 2, N.FLOAT, !1, 0, 0),
        N.drawArrays(N.TRIANGLE_STRIP, 0, 4)
    }
    ,
    $.getDefaultShader = function() {
        return N.defaultShader = N.defaultShader || new $,
        N.defaultShader
    }
    ;
    var j = $
      , q = "float random(vec3 scale,float seed){return fract(sin(dot(gl_FragCoord.xyz+seed,scale))*43758.5453+seed);}";
    function J(t, e) {
        if (t = N.createShader(t),
        N.shaderSource(t, e),
        N.compileShader(t),
        N.getShaderParameter(t, N.COMPILE_STATUS))
            return t;
        throw "compile error: " + N.getShaderInfoLog(t)
    }
    function $(t, e) {
        if (this.texCoordAttribute = this.vertexAttribute = null,
        this.program = N.createProgram(),
        e = "precision highp float;" + (e = e || "uniform sampler2D texture;varying vec2 texCoord;void main(){gl_FragColor=texture2D(texture,texCoord);}"),
        N.attachShader(this.program, J(N.VERTEX_SHADER, t = t || "attribute vec2 vertex;attribute vec2 _texCoord;varying vec2 texCoord;void main(){texCoord=_texCoord;gl_Position=vec4(vertex*2.0-1.0,0.0,1.0);}")),
        N.attachShader(this.program, J(N.FRAGMENT_SHADER, e)),
        N.linkProgram(this.program),
        !N.getProgramParameter(this.program, N.LINK_STATUS))
            throw "link error: " + N.getProgramInfoLog(this.program)
    }
    return O
}();
"object" == typeof module ? module.exports = fx : window.fx = fx,
function() {
    function t(e) {
        return e instanceof t ? e : this instanceof t ? void (this.EXIFwrapped = e) : new t(e)
    }
    var e = ("undefined" != typeof exports ? (exports = "undefined" != typeof module && module.exports ? module.exports = t : exports).EXIF = t : this.EXIF = t,
    t.Tags = {
        36864: "ExifVersion",
        40960: "FlashpixVersion",
        40961: "ColorSpace",
        40962: "PixelXDimension",
        40963: "PixelYDimension",
        37121: "ComponentsConfiguration",
        37122: "CompressedBitsPerPixel",
        37500: "MakerNote",
        37510: "UserComment",
        40964: "RelatedSoundFile",
        36867: "DateTimeOriginal",
        36868: "DateTimeDigitized",
        37520: "SubsecTime",
        37521: "SubsecTimeOriginal",
        37522: "SubsecTimeDigitized",
        33434: "ExposureTime",
        33437: "FNumber",
        34850: "ExposureProgram",
        34852: "SpectralSensitivity",
        34855: "ISOSpeedRatings",
        34856: "OECF",
        37377: "ShutterSpeedValue",
        37378: "ApertureValue",
        37379: "BrightnessValue",
        37380: "ExposureBias",
        37381: "MaxApertureValue",
        37382: "SubjectDistance",
        37383: "MeteringMode",
        37384: "LightSource",
        37385: "Flash",
        37396: "SubjectArea",
        37386: "FocalLength",
        41483: "FlashEnergy",
        41484: "SpatialFrequencyResponse",
        41486: "FocalPlaneXResolution",
        41487: "FocalPlaneYResolution",
        41488: "FocalPlaneResolutionUnit",
        41492: "SubjectLocation",
        41493: "ExposureIndex",
        41495: "SensingMethod",
        41728: "FileSource",
        41729: "SceneType",
        41730: "CFAPattern",
        41985: "CustomRendered",
        41986: "ExposureMode",
        41987: "WhiteBalance",
        41988: "DigitalZoomRation",
        41989: "FocalLengthIn35mmFilm",
        41990: "SceneCaptureType",
        41991: "GainControl",
        41992: "Contrast",
        41993: "Saturation",
        41994: "Sharpness",
        41995: "DeviceSettingDescription",
        41996: "SubjectDistanceRange",
        40965: "InteroperabilityIFDPointer",
        42016: "ImageUniqueID"
    })
      , r = t.TiffTags = {
        256: "ImageWidth",
        257: "ImageHeight",
        34665: "ExifIFDPointer",
        34853: "GPSInfoIFDPointer",
        40965: "InteroperabilityIFDPointer",
        258: "BitsPerSample",
        259: "Compression",
        262: "PhotometricInterpretation",
        274: "Orientation",
        277: "SamplesPerPixel",
        284: "PlanarConfiguration",
        530: "YCbCrSubSampling",
        531: "YCbCrPositioning",
        282: "XResolution",
        283: "YResolution",
        296: "ResolutionUnit",
        273: "StripOffsets",
        278: "RowsPerStrip",
        279: "StripByteCounts",
        513: "JPEGInterchangeFormat",
        514: "JPEGInterchangeFormatLength",
        301: "TransferFunction",
        318: "WhitePoint",
        319: "PrimaryChromaticities",
        529: "YCbCrCoefficients",
        532: "ReferenceBlackWhite",
        306: "DateTime",
        270: "ImageDescription",
        271: "Make",
        272: "Model",
        305: "Software",
        315: "Artist",
        33432: "Copyright"
    }
      , o = t.GPSTags = {
        0: "GPSVersionID",
        1: "GPSLatitudeRef",
        2: "GPSLatitude",
        3: "GPSLongitudeRef",
        4: "GPSLongitude",
        5: "GPSAltitudeRef",
        6: "GPSAltitude",
        7: "GPSTimeStamp",
        8: "GPSSatellites",
        9: "GPSStatus",
        10: "GPSMeasureMode",
        11: "GPSDOP",
        12: "GPSSpeedRef",
        13: "GPSSpeed",
        14: "GPSTrackRef",
        15: "GPSTrack",
        16: "GPSImgDirectionRef",
        17: "GPSImgDirection",
        18: "GPSMapDatum",
        19: "GPSDestLatitudeRef",
        20: "GPSDestLatitude",
        21: "GPSDestLongitudeRef",
        22: "GPSDestLongitude",
        23: "GPSDestBearingRef",
        24: "GPSDestBearing",
        25: "GPSDestDistanceRef",
        26: "GPSDestDistance",
        27: "GPSProcessingMethod",
        28: "GPSAreaInformation",
        29: "GPSDateStamp",
        30: "GPSDifferential"
    }
      , i = t.IFD1Tags = {
        256: "ImageWidth",
        257: "ImageHeight",
        258: "BitsPerSample",
        259: "Compression",
        262: "PhotometricInterpretation",
        273: "StripOffsets",
        274: "Orientation",
        277: "SamplesPerPixel",
        278: "RowsPerStrip",
        279: "StripByteCounts",
        282: "XResolution",
        283: "YResolution",
        284: "PlanarConfiguration",
        296: "ResolutionUnit",
        513: "JpegIFOffset",
        514: "JpegIFByteCount",
        529: "YCbCrCoefficients",
        530: "YCbCrSubSampling",
        531: "YCbCrPositioning",
        532: "ReferenceBlackWhite"
    }
      , a = t.StringValues = {
        ExposureProgram: {
            0: "Not defined",
            1: "Manual",
            2: "Normal program",
            3: "Aperture priority",
            4: "Shutter priority",
            5: "Creative program",
            6: "Action program",
            7: "Portrait mode",
            8: "Landscape mode"
        },
        MeteringMode: {
            0: "Unknown",
            1: "Average",
            2: "CenterWeightedAverage",
            3: "Spot",
            4: "MultiSpot",
            5: "Pattern",
            6: "Partial",
            255: "Other"
        },
        LightSource: {
            0: "Unknown",
            1: "Daylight",
            2: "Fluorescent",
            3: "Tungsten (incandescent light)",
            4: "Flash",
            9: "Fine weather",
            10: "Cloudy weather",
            11: "Shade",
            12: "Daylight fluorescent (D 5700 - 7100K)",
            13: "Day white fluorescent (N 4600 - 5400K)",
            14: "Cool white fluorescent (W 3900 - 4500K)",
            15: "White fluorescent (WW 3200 - 3700K)",
            17: "Standard light A",
            18: "Standard light B",
            19: "Standard light C",
            20: "D55",
            21: "D65",
            22: "D75",
            23: "D50",
            24: "ISO studio tungsten",
            255: "Other"
        },
        Flash: {
            0: "Flash did not fire",
            1: "Flash fired",
            5: "Strobe return light not detected",
            7: "Strobe return light detected",
            9: "Flash fired, compulsory flash mode",
            13: "Flash fired, compulsory flash mode, return light not detected",
            15: "Flash fired, compulsory flash mode, return light detected",
            16: "Flash did not fire, compulsory flash mode",
            24: "Flash did not fire, auto mode",
            25: "Flash fired, auto mode",
            29: "Flash fired, auto mode, return light not detected",
            31: "Flash fired, auto mode, return light detected",
            32: "No flash function",
            65: "Flash fired, red-eye reduction mode",
            69: "Flash fired, red-eye reduction mode, return light not detected",
            71: "Flash fired, red-eye reduction mode, return light detected",
            73: "Flash fired, compulsory flash mode, red-eye reduction mode",
            77: "Flash fired, compulsory flash mode, red-eye reduction mode, return light not detected",
            79: "Flash fired, compulsory flash mode, red-eye reduction mode, return light detected",
            89: "Flash fired, auto mode, red-eye reduction mode",
            93: "Flash fired, auto mode, return light not detected, red-eye reduction mode",
            95: "Flash fired, auto mode, return light detected, red-eye reduction mode"
        },
        SensingMethod: {
            1: "Not defined",
            2: "One-chip color area sensor",
            3: "Two-chip color area sensor",
            4: "Three-chip color area sensor",
            5: "Color sequential area sensor",
            7: "Trilinear sensor",
            8: "Color sequential linear sensor"
        },
        SceneCaptureType: {
            0: "Standard",
            1: "Landscape",
            2: "Portrait",
            3: "Night scene"
        },
        SceneType: {
            1: "Directly photographed"
        },
        CustomRendered: {
            0: "Normal process",
            1: "Custom process"
        },
        WhiteBalance: {
            0: "Auto white balance",
            1: "Manual white balance"
        },
        GainControl: {
            0: "None",
            1: "Low gain up",
            2: "High gain up",
            3: "Low gain down",
            4: "High gain down"
        },
        Contrast: {
            0: "Normal",
            1: "Soft",
            2: "Hard"
        },
        Saturation: {
            0: "Normal",
            1: "Low saturation",
            2: "High saturation"
        },
        Sharpness: {
            0: "Normal",
            1: "Soft",
            2: "Hard"
        },
        SubjectDistanceRange: {
            0: "Unknown",
            1: "Macro",
            2: "Close view",
            3: "Distant view"
        },
        FileSource: {
            3: "DSC"
        },
        Components: {
            0: "",
            1: "Y",
            2: "Cb",
            3: "Cr",
            4: "R",
            5: "G",
            6: "B"
        }
    };
    function l(t) {
        return t.exifdata
    }
    function s(t) {
        var n = new DataView(t);
        if (255 != n.getUint8(0) || 216 != n.getUint8(1))
            return !1;
        for (var l = 2, s = t.byteLength; l < s; ) {
            if (255 != n.getUint8(l))
                return !1;
            if (225 == (p = n.getUint8(l + 1))) {
                var c, f, d, m, g, p = n, x = l + 4;
                if (n.getUint16(l + 2),
                "Exif" != h(p, x, 4))
                    return !1;
                if (x += 6,
                18761 == p.getUint16(x))
                    c = !1;
                else {
                    if (19789 != p.getUint16(x))
                        return !1;
                    c = !0
                }
                if (42 != p.getUint16(x + 2, !c))
                    return !1;
                var v = p.getUint32(x + 4, !c);
                if (v < 8)
                    return !1;
                if ((f = u(p, x, x + v, r, c)).ExifIFDPointer)
                    for (d in m = u(p, x, x + f.ExifIFDPointer, e, c)) {
                        switch (d) {
                        case "LightSource":
                        case "Flash":
                        case "MeteringMode":
                        case "ExposureProgram":
                        case "SensingMethod":
                        case "SceneCaptureType":
                        case "SceneType":
                        case "CustomRendered":
                        case "WhiteBalance":
                        case "GainControl":
                        case "Contrast":
                        case "Saturation":
                        case "Sharpness":
                        case "SubjectDistanceRange":
                        case "FileSource":
                            m[d] = a[d][m[d]];
                            break;
                        case "ExifVersion":
                        case "FlashpixVersion":
                            m[d] = String.fromCharCode(m[d][0], m[d][1], m[d][2], m[d][3]);
                            break;
                        case "ComponentsConfiguration":
                            m[d] = a.Components[m[d][0]] + a.Components[m[d][1]] + a.Components[m[d][2]] + a.Components[m[d][3]]
                        }
                        f[d] = m[d]
                    }
                if (f.GPSInfoIFDPointer)
                    for (d in g = u(p, x, x + f.GPSInfoIFDPointer, o, c))
                        "GPSVersionID" === d && (g[d] = g[d][0] + "." + g[d][1] + "." + g[d][2] + "." + g[d][3]),
                        f[d] = g[d];
                return f.thumbnail = function(t, e, r, o) {
                    if (r = function(t, e, r) {
                        var o = t.getUint16(e, !r);
                        return t.getUint32(e + 2 + 12 * o, !r)
                    }(t, e + r, o),
                    !r)
                        return {};
                    if (r > t.byteLength)
                        return {};
                    var a = u(t, e, e + r, i, o);
                    if (a.Compression)
                        switch (a.Compression) {
                        case 6:
                            var n, l;
                            a.JpegIFOffset && a.JpegIFByteCount && (n = e + a.JpegIFOffset,
                            l = a.JpegIFByteCount,
                            a.blob = new Blob([new Uint8Array(t.buffer,n,l)],{
                                type: "image/jpeg"
                            }));
                            break;
                        case 1:
                            console.log("Thumbnail image format is TIFF, which is not implemented.");
                            break;
                        default:
                            console.log("Unknown thumbnail image format '%s'", a.Compression)
                        }
                    else
                        2 == a.PhotometricInterpretation && console.log("Thumbnail image format is RGB, which is not implemented.");
                    return a
                }(p, x, v, c),
                f
            }
            l += 2 + n.getUint16(l + 2)
        }
    }
    var c = {
        120: "caption",
        110: "credit",
        25: "keywords",
        55: "dateCreated",
        80: "byline",
        85: "bylineTitle",
        122: "captionWriter",
        105: "headline",
        116: "copyright",
        15: "category"
    };
    function u(t, e, r, o, i) {
        for (var a, n = t.getUint16(r, !i), l = {}, s = 0; s < n; s++)
            l[o[t.getUint16(a = r + 12 * s + 2, !i)]] = function(t, e, r, o) {
                var i, a, n, l, s, c, u = t.getUint16(e + 2, !o), f = t.getUint32(e + 4, !o), d = t.getUint32(e + 8, !o) + r;
                switch (u) {
                case 1:
                case 7:
                    if (1 == f)
                        return t.getUint8(e + 8, !o);
                    for (i = 4 < f ? d : e + 8,
                    a = [],
                    l = 0; l < f; l++)
                        a[l] = t.getUint8(i + l);
                    return a;
                case 2:
                    return h(t, i = 4 < f ? d : e + 8, f - 1);
                case 3:
                    if (1 == f)
                        return t.getUint16(e + 8, !o);
                    for (i = 2 < f ? d : e + 8,
                    a = [],
                    l = 0; l < f; l++)
                        a[l] = t.getUint16(i + 2 * l, !o);
                    return a;
                case 4:
                    if (1 == f)
                        return t.getUint32(e + 8, !o);
                    for (a = [],
                    l = 0; l < f; l++)
                        a[l] = t.getUint32(d + 4 * l, !o);
                    return a;
                case 5:
                    if (1 == f)
                        return s = t.getUint32(d, !o),
                        c = t.getUint32(d + 4, !o),
                        (n = new Number(s / c)).numerator = s,
                        n.denominator = c,
                        n;
                    for (a = [],
                    l = 0; l < f; l++)
                        s = t.getUint32(d + 8 * l, !o),
                        c = t.getUint32(d + 4 + 8 * l, !o),
                        a[l] = new Number(s / c),
                        a[l].numerator = s,
                        a[l].denominator = c;
                    return a;
                case 9:
                    if (1 == f)
                        return t.getInt32(e + 8, !o);
                    for (a = [],
                    l = 0; l < f; l++)
                        a[l] = t.getInt32(d + 4 * l, !o);
                    return a;
                case 10:
                    if (1 == f)
                        return t.getInt32(d, !o) / t.getInt32(d + 4, !o);
                    for (a = [],
                    l = 0; l < f; l++)
                        a[l] = t.getInt32(d + 8 * l, !o) / t.getInt32(d + 4 + 8 * l, !o);
                    return a
                }
            }(t, a, e, i);
        return l
    }
    function h(t, e, r) {
        var o = "";
        for (n = e; n < e + r; n++)
            o += String.fromCharCode(t.getUint8(n));
        return o
    }
    function f(t) {
        var e = {};
        if (1 == t.nodeType) {
            if (0 < t.attributes.length) {
                e["@attributes"] = {};
                for (var r = 0; r < t.attributes.length; r++) {
                    var o = t.attributes.item(r);
                    e["@attributes"][o.nodeName] = o.nodeValue
                }
            }
        } else if (3 == t.nodeType)
            return t.nodeValue;
        if (t.hasChildNodes())
            for (var i = 0; i < t.childNodes.length; i++) {
                var a, n = t.childNodes.item(i), l = n.nodeName;
                null == e[l] ? e[l] = f(n) : (null == e[l].push && (a = e[l],
                e[l] = [],
                e[l].push(a)),
                e[l].push(f(n)))
            }
        return e
    }
    t.enableXmp = function() {
        t.isXmpEnabled = !0
    }
    ,
    t.disableXmp = function() {
        t.isXmpEnabled = !1
    }
    ,
    t.getData = function(e, r) {
        return !((self.Image && e instanceof self.Image || self.HTMLImageElement && e instanceof self.HTMLImageElement) && !e.complete || (l(e) ? r && r.call(e) : function(e, r) {
            function o(o) {
                var i = s(o);
                e.exifdata = i || {},
                i = function(t) {
                    var e = new DataView(t);
                    if (255 != e.getUint8(0) || 216 != e.getUint8(1))
                        return !1;
                    for (var r = 2, o = t.byteLength; r < o; ) {
                        var i;
                        if (function(t, e) {
                            return 56 === t.getUint8(e) && 66 === t.getUint8(e + 1) && 73 === t.getUint8(e + 2) && 77 === t.getUint8(e + 3) && 4 === t.getUint8(e + 4) && 4 === t.getUint8(e + 5)
                        }(e, r))
                            return (i = e.getUint8(r + 7)) % 2 != 0 && (i += 1),
                            function(t, e, r) {
                                for (var o, i, a = new DataView(t), n = {}, l = e; l < e + r; )
                                    28 === a.getUint8(l) && 2 === a.getUint8(l + 1) && (i = a.getUint8(l + 2))in c && (o = a.getInt16(l + 3),
                                    i = c[i],
                                    o = h(a, l + 5, o),
                                    n.hasOwnProperty(i) ? n[i]instanceof Array ? n[i].push(o) : n[i] = [n[i], o] : n[i] = o),
                                    l++;
                                return n
                            }(t, r + 8 + (i = 0 === i ? 4 : i), i = e.getUint16(r + 6 + i));
                        r++
                    }
                }(o),
                e.iptcdata = i || {},
                t.isXmpEnabled && (i = function(t) {
                    if ("DOMParser"in self) {
                        var e = new DataView(t);
                        if (255 != e.getUint8(0) || 216 != e.getUint8(1))
                            return !1;
                        for (var r, o, i = 2, a = t.byteLength, n = new DOMParser; i < a - 4; ) {
                            if ("http" == h(e, i, 4))
                                return r = i - 1,
                                o = e.getUint16(i - 2) - 1,
                                o = (r = h(e, r, o)).indexOf("xmpmeta>") + 8,
                                o = (r = r.substring(r.indexOf("<x:xmpmeta"), o)).indexOf("x:xmpmeta") + 10,
                                r = r.slice(0, o) + 'xmlns:Iptc4xmpCore="http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:tiff="http://ns.adobe.com/tiff/1.0/" xmlns:plus="http://schemas.android.com/apk/lib/com.google.android.gms.plus" xmlns:ext="http://www.gettyimages.com/xsltExtension/1.0" xmlns:exif="http://ns.adobe.com/exif/1.0/" xmlns:stEvt="http://ns.adobe.com/xap/1.0/sType/ResourceEvent#" xmlns:stRef="http://ns.adobe.com/xap/1.0/sType/ResourceRef#" xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/" xmlns:xapGImg="http://ns.adobe.com/xap/1.0/g/img/" xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/" ' + r.slice(o),
                                function(t) {
                                    try {
                                        var e = {};
                                        if (0 < t.children.length)
                                            for (var r = 0; r < t.children.length; r++) {
                                                var o, i = t.children.item(r), a = i.attributes;
                                                for (o in a) {
                                                    var n = a[o]
                                                      , l = n.nodeName
                                                      , s = n.nodeValue;
                                                    void 0 !== l && (e[l] = s)
                                                }
                                                var c, u = i.nodeName;
                                                void 0 === e[u] ? e[u] = f(i) : (void 0 === e[u].push && (c = e[u],
                                                e[u] = [],
                                                e[u].push(c)),
                                                e[u].push(f(i)))
                                            }
                                        else
                                            e = t.textContent;
                                        return e
                                    } catch (t) {
                                        console.log(t.message)
                                    }
                                }(n.parseFromString(r, "text/xml"));
                            i++
                        }
                    }
                }(o),
                e.xmpdata = i || {}),
                r && r.call(e)
            }
            var i, a, n, l, u;
            e.src ? /^data\:/i.test(e.src) ? o(function(t, e) {
                e = e || t.match(/^data\:([^\;]+)\;base64,/im)[1] || "",
                t = t.replace(/^data\:([^\;]+)\;base64,/gim, "");
                for (var r = atob(t), o = r.length, i = (e = new ArrayBuffer(o),
                new Uint8Array(e)), a = 0; a < o; a++)
                    i[a] = r.charCodeAt(a);
                return e
            }(e.src)) : /^blob\:/i.test(e.src) ? ((a = new FileReader).onload = function(t) {
                o(t.target.result)
            }
            ,
            n = e.src,
            l = function(t) {
                a.readAsArrayBuffer(t)
            }
            ,
            (u = new XMLHttpRequest).open("GET", n, !0),
            u.responseType = "blob",
            u.onload = function(t) {
                200 != this.status && 0 !== this.status || l(this.response)
            }
            ,
            u.send()) : ((i = new XMLHttpRequest).onload = function() {
                if (200 != this.status && 0 !== this.status)
                    throw "Could not load image";
                o(i.response),
                i = null
            }
            ,
            i.open("GET", e.src, !0),
            i.responseType = "arraybuffer",
            i.send(null)) : self.FileReader && (e instanceof self.Blob || e instanceof self.File) && ((a = new FileReader).onload = function(t) {
                o(t.target.result)
            }
            ,
            a.readAsArrayBuffer(e))
        }(e, r),
        0))
    }
    ,
    t.getTag = function(t, e) {
        if (l(t))
            return t.exifdata[e]
    }
    ,
    t.getIptcTag = function(t, e) {
        if (l(t))
            return t.iptcdata[e]
    }
    ,
    t.getAllTags = function(t) {
        if (!l(t))
            return {};
        var e, r = t.exifdata, o = {};
        for (e in r)
            r.hasOwnProperty(e) && (o[e] = r[e]);
        return o
    }
    ,
    t.getAllIptcTags = function(t) {
        if (!l(t))
            return {};
        var e, r = t.iptcdata, o = {};
        for (e in r)
            r.hasOwnProperty(e) && (o[e] = r[e]);
        return o
    }
    ,
    t.pretty = function(t) {
        if (!l(t))
            return "";
        var e, r = t.exifdata, o = "";
        for (e in r)
            r.hasOwnProperty(e) && ("object" == typeof r[e] ? r[e]instanceof Number ? o += e + " : " + r[e] + " [" + r[e].numerator + "/" + r[e].denominator + "]\r\n" : o += e + " : [" + r[e].length + " values]\r\n" : o += e + " : " + r[e] + "\r\n");
        return o
    }
    ,
    t.readFromBinaryFile = s,
    "function" == typeof define && define.amd && define("exif-js", [], (function() {
        return t
    }
    ))
}
.call(this);
