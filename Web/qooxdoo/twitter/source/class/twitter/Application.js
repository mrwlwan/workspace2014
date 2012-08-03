/* ************************************************************************

   Copyright:

   License:

   Authors:

************************************************************************ */

/* ************************************************************************

#asset(twitter/*)

************************************************************************ */

/**
 * This is the main application class of your custom application "twitter"
 */
qx.Class.define("twitter.Application",
{
  extend : qx.application.Standalone,



  /*
  *****************************************************************************
     MEMBERS
  *****************************************************************************
  */

  members :
  {
    /**
     * This method contains the initial application code and gets called 
     * during startup of the application
     * 
     * @lint ignoreDeprecated(alert)
     */
    main : function()
    {
      // Call super class
      this.base(arguments);

      // Enable logging in debug variant
      if (qx.core.Environment.get("qx.debug"))
      {
        // support native logging capabilities, e.g. Firebug for Firefox
        qx.log.appender.Native;
        // support additional cross-browser console. Press F7 to toggle visibility
        qx.log.appender.Console;
      }

      /*
      -------------------------------------------------------------------------
        Below is your actual application code...
      -------------------------------------------------------------------------
      */
    var main = new twitter.MainWindow();
    main.addListener('post', function(e){
        this.debug('post:' + e.getData());
    }, this);
    main.open();
    main.moveTo(50, 30);

    var service = new twitter.TwitterService();

    main.addListener('reload', function(){
        service.fetchTweets();
    }, this);

    service.addListener('changeTweets', function(e){
        this.debug(qx.dev.Debug.debugProperties(e.getData()));
    }, this);
    
    var controller = new qx.data.controller.List(null, main.getList());
    controller.setLabelPath('text');
    controller.setIconPath('user.profile_image_url');
    controller.setDelegate({
        configureItem: function(item){
            item.getChildControl('icon').setWidth(48);
            item.getChildControl('icon').setHeight(48);
            item.getChildControl('icon').setScale(true);
            item.setRich(true);
        }
    });
    service.bind('tweets', controller, 'model');
    service.fetchTweets();
    }
  }
});
