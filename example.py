import whatsapp

client = whatsapp.client.WhatsappClient()


@client.command("stop", help_message="Stops the bot")
def stop(args, msg_obj: whatsapp.message.Message):
    if msg_obj.sender["this_person"]:
        client.send_message("Stopping bot...")
        client.stop()
    else:
        client.send_message("You are not allowed to do this.")


@client.on_message
def greeting(msg_obj: whatsapp.message.Message):
    if not msg_obj.sender["this_person"]:
        if msg_obj.contents.lower() == "hi":
            client.send_message("Hi")


client.run()
