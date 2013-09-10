(function() {
  window.Packages = {};

  window.Packages.initializeCountdown = function(selector, initialDateTime) {
    console.log($(selector).html());
    return $(selector).countdown({
      date: initialDateTime,
      refresh: 1000,
      render: function(data) {
        return $(this.el).text(data.days >= 1 ? data.days + " day" + (data.days > 1 ? "s" : "") : data.min >= 1 ? this.leadingZeros(data.hours, 2) + " hour" + (data.hours > 1 ? "s" : "") + " " + this.leadingZeros(data.min, 2) + " min" + (data.min > 1 ? "s" : "") : this.leadingZeros(data.sec, 2) + " second" + (data.sec > 1 ? "s" : ""));
      }
    });
  };

}).call(this);

/*
countdown is a simple jquery plugin for countdowns

Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php)
and GPL-3.0 (http://opensource.org/licenses/GPL-3.0) licenses.

@source: http://github.com/rendro/countdown/
@autor: Robert Fleischmann
@version: 1.0.1
*/


(function() {
  (function($) {
    $.countdown = function(el, options) {
      var getDateData,
        _this = this;
      this.el = el;
      this.$el = $(el);
      this.$el.data("countdown", this);
      this.init = function() {
        _this.options = $.extend({}, $.countdown.defaultOptions, options);
        if (_this.options.refresh) {
          _this.interval = setInterval(function() {
            return _this.render();
          }, _this.options.refresh);
        }
        _this.render();
        return _this;
      };
      getDateData = function(endDate) {
        var dateData, diff;
        endDate = Date.parse($.isPlainObject(_this.options.date) ? _this.options.date : new Date(_this.options.date));
        diff = (endDate - Date.parse(new Date)) / 1000;
        if (diff <= 0) {
          diff = 0;
          if (_this.interval) {
            _this.stop();
          }
          _this.options.onEnd.apply(_this);
        }
        dateData = {
          years: 0,
          days: 0,
          hours: 0,
          min: 0,
          sec: 0,
          millisec: 0
        };
        if (diff >= (365.25 * 86400)) {
          dateData.years = Math.floor(diff / (365.25 * 86400));
          diff -= dateData.years * 365.25 * 86400;
        }
        if (diff >= 86400) {
          dateData.days = Math.floor(diff / 86400);
          diff -= dateData.days * 86400;
        }
        if (diff >= 3600) {
          dateData.hours = Math.floor(diff / 3600);
          diff -= dateData.hours * 3600;
        }
        if (diff >= 60) {
          dateData.min = Math.floor(diff / 60);
          diff -= dateData.min * 60;
        }
        dateData.sec = diff;
        return dateData;
      };
      this.leadingZeros = function(num, length) {
        if (length == null) {
          length = 2;
        }
        num = String(num);
        while (num.length < length) {
          num = "0" + num;
        }
        return num;
      };
      this.update = function(newDate) {
        _this.options.date = newDate;
        return _this;
      };
      this.render = function() {
        _this.options.render.apply(_this, [getDateData(_this.options.date)]);
        return _this;
      };
      this.stop = function() {
        if (_this.interval) {
          clearInterval(_this.interval);
        }
        _this.interval = null;
        return _this;
      };
      this.start = function(refresh) {
        if (refresh == null) {
          refresh = _this.options.refresh || $.countdown.defaultOptions.refresh;
        }
        if (_this.interval) {
          clearInterval(_this.interval);
        }
        _this.render();
        _this.options.refresh = refresh;
        _this.interval = setInterval(function() {
          return _this.render();
        }, _this.options.refresh);
        return _this;
      };
      return this.init();
    };
    $.countdown.defaultOptions = {
      date: "June 7, 2087 15:03:25",
      refresh: 1000,
      onEnd: $.noop,
      render: function(date) {
        return $(this.el).html("" + date.years + " years, " + date.days + " days, " + (this.leadingZeros(date.hours)) + " hours, " + (this.leadingZeros(date.min)) + " min and " + (this.leadingZeros(date.sec)) + " sec");
      }
    };
    $.fn.countdown = function(options) {
      return $.each(this, function(i, el) {
        var $el;
        $el = $(el);
        if (!$el.data('countdown')) {
          return $el.data('countdown', new $.countdown(el, options));
        }
      });
    };
    return void 0;
  })(jQuery);

}).call(this);