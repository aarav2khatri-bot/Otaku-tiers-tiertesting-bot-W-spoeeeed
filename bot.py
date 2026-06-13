import discord
from discord import ui, app_commands, SelectOption
import json
import os
import asyncio
import random
import string
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

CONFIG = {
    "tester_role": None,
    "high_tester_role": None,
    "admin_role": None,
    "staff_role": None,
    "helper_role": None,
    "gamemode_channels": {}
}

# ====================== TICKET SYSTEM ======================
class TicketTypeSelect(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🤝 Partnership", style=discord.ButtonStyle.primary, emoji="🤝", custom_id="ticket_partnership")
    async def partnership(self, interaction: discord.Interaction, button):
        await self.create_ticket(interaction, "Partnership")

    @ui.button(label="❓ Support", style=discord.ButtonStyle.green, emoji="❓", custom_id="ticket_support")
    async def support(self, interaction: discord.Interaction, button):
        await self.create_ticket(interaction, "Support")

    @ui.button(label="🚨 Staff Abuse", style=discord.ButtonStyle.red, emoji="🚨", custom_id="ticket_abuse")
    async def abuse(self, interaction: discord.Interaction, button):
        await self.create_ticket(interaction, "Staff Abuse")

    @ui.button(label="🎁 Redeem Rewards", style=discord.ButtonStyle.gray, emoji="🎁", custom_id="ticket_redeem")
    async def redeem(self, interaction: discord.Interaction, button):
        await self.create_ticket(interaction, "Redeem Rewards")

    @ui.button(label="📢 Advertisement", style=discord.ButtonStyle.blurple, emoji="📢", custom_id="ticket_ad")
    async def ad(self, interaction: discord.Interaction, button):
        await self.create_ticket(interaction, "Advertisement")

    @ui.button(label="⚖️ Appeal", style=discord.ButtonStyle.gray, emoji="⚖️", custom_id="ticket_appeal")
    async def appeal(self, interaction: discord.Interaction, button):
        await self.create_ticket(interaction, "Appeal")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        category = discord.utils.get(interaction.guild.categories, name="Tickets") or await interaction.guild.create_category("Tickets")
        
        staff_role = discord.utils.get(interaction.guild.roles, id=CONFIG.get("staff_role"))
        helper_role = discord.utils.get(interaction.guild.roles, id=CONFIG.get("helper_role"))

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        if helper_role:
            overwrites[helper_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket = await interaction.guild.create_text_channel(f"{ticket_type.lower()}-{interaction.user.name}", category=category, overwrites=overwrites)

        embed = discord.Embed(title=f"{ticket_type} Ticket", description=f"Created by {interaction.user.mention}\n\nPlease describe your request.", color=0x00FFFF)
        await ticket.send(embed=embed)

        await interaction.response.send_message(f"✅ {ticket_type} ticket created: {ticket.mention}", ephemeral=True)

# ====================== SUPPORT PANEL ======================
async def create_support_panel(channel):
    embed = discord.Embed(
        title="🎟️ Ticket System",
        description="Select the appropriate ticket type below.\n\n"
                    "🤝 **Partnership** — Interested in partnering with us?\n"
                    "❓ **Support** — Need help with something?\n"
                    "🚨 **Staff Abuse** — Report staff misconduct.\n"
                    "🎁 **Redeem Rewards** — Claim your earned rewards.\n"
                    "📢 **Advertisement** — Want to advertise?\n"
                    "⚖️ **Appeal** — Appeal a punishment.\n\n"
                    "**Please have all necessary information ready before opening a ticket.**\n\n"
                    "-# Creating Tickets For Fun Will Lead To PUNISHMENT.",
        color=0x00FFFF
    )
    view = TicketTypeSelect()
    await channel.send(embed=embed, view=view)

# ====================== PANEL COMMAND ======================
@tree.command(name="panel", description="Create panel")
@app_commands.choices(panel_type=[
    app_commands.Choice(name="evaluation", value="evaluation"),
    app_commands.Choice(name="high_test", value="high_test"),
    app_commands.Choice(name="tickets", value="tickets")
])
async def panel_cmd(interaction: discord.Interaction, panel_type: str, channel: discord.TextChannel):
    if panel_type == "tickets":
        await create_support_panel(channel)
    # Add other panels...
    await interaction.response.send_message("✅ Panel created!", ephemeral=True)

# ====================== SETUP ROLE ======================
@tree.command(name="setup_role", description="Setup all roles")
async def setup_role(
    interaction: discord.Interaction,
    tester: discord.Role,
    high_tester: discord.Role,
    admin: discord.Role,
    staff: discord.Role,
    helper: discord.Role
):
    CONFIG["tester_role"] = tester.id
    CONFIG["high_tester_role"] = high_tester.id
    CONFIG["admin_role"] = admin.id
    CONFIG["staff_role"] = staff.id
    CONFIG["helper_role"] = helper.id
    save_data()
    await interaction.response.send_message("✅ All roles saved!\nStaff + Helper can view all tickets.", ephemeral=True)

# ====================== CLOSE TICKET ======================
@tree.command(name="close_ticket", description="Close current ticket")
async def close_ticket(interaction: discord.Interaction):
    if not interaction.channel.category or interaction.channel.category.name != "Tickets":
        return await interaction.response.send_message("❌ Use this inside a ticket.", ephemeral=True)

    await interaction.response.send_message("✅ Closing ticket in 3 seconds...", ephemeral=True)
    await asyncio.sleep(3)
    try:
        await interaction.channel.delete()
    except:
        await interaction.followup.send("Could not delete channel.", ephemeral=True)

# Keep Alive for Railway
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.run(os.getenv("TOKEN"))
