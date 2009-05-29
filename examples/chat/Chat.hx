/** FMSPy - Copyright (c) 2009 Andrey Smirnov.
 *
 * See COPYRIGHT for details.
 *
 * Chat example application - Flash part.
 * Based on haxe examples.
 */

class Chat {

	var name : String;
	var tf : flash.TextField;
	var log : flash.TextField;
    var connection : flash.NetConnection;

	function new() 
    {
        connection = new flash.NetConnection();
        connection.onStatus = onStatus;
        connection.connect("rtmp://localhost/chat");
        connection.message = message;
	}

    function onStatus (info)
    {
            if (info.code == "NetConnection.Connect.Success")
            {
                connected();
            }
            else
                trace("status: " + info.code); 
    }

    function message (text)
    {
		display(text.split("&").join("&amp;").split("<").join("&lt;").split(">").join("&gt;"));
    }

	function connected() 
    {
		// create an input textfield
		tf = flash.Lib.current.createTextField("tf",0,5,flash.Stage.height - 25,flash.Stage.width-10,20);
		tf.type = "input";
		tf.border = true;
		tf.background = true;
		tf.backgroundColor = 0xEEEEEE;
		flash.Key.onKeyDown = onKeyDown;
		// create a chat log
		log = flash.Lib.current.createTextField("log",1,5,5,flash.Stage.width-10,flash.Stage.height - 35);
		log.background = true;
		log.backgroundColor = 0xFFFFFF;
		log.html = true;
		log.border = true;
		log.multiline = true;
		display("Please enter your name in the bottom textfield to login and press ENTER");
	}

	function onKeyDown() {
		// ENTER pressed ?
		if( flash.Key.getCode() == 13 ) {
			var text = tf.text;
			tf.text = "";
			send(text);
		}
	}

	function send( text : String ) {
		if( name == null ) {
			name = text;
			connection.call('identify', this, name);
			return;
		}
		connection.call('say', this, text);
	}

	function display( line : String ) {
		var bottom = (log.scroll == log.maxscroll);
		log.htmlText += line + "<br>";
		if( bottom )
			log.scroll = log.maxscroll;
	}

	// --

	static var c : Chat;

	static function main() {
		c = new Chat();
	}

}
