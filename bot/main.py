import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
from predict import predict_health_risks
import pandas as pd
import os

def save_user_data_csv(user_id, session_data):
    data = {
        "UserID": user_id,
        "Name": session_data.get("Name", ""),
        "Age": session_data.get("Age", ""),
        "Gender": "Male" if session_data.get("Gender") == 1 else "Female",
        "Height_cm": session_data.get("Height", ""),
        "Weight_kg": session_data.get("Weight", ""),
        "BMI": session_data.get("BMI", ""),
        "Sleep_hours": session_data.get("Sleep_hours", ""),
        "Activity_minutes": session_data.get("Physical_activity_mins", ""),
        "Water_intake_liters": session_data.get("Water_intake_liters", ""),
        "Junk_food_per_week": session_data.get("Junk_food_per_week", ""),
        "Fruit_veggies_per_day": session_data.get("Fruit_veggies_per_day", ""),
        "Family_history": session_data.get("Family_history", ""),
        "Lifestyle": session_data.get("Lifestyle", ""),
        "Lifestyle_freq": session_data.get("Lifestyle_freq", ""),
    }

    # Add prediction results if available
    if "Predictions" in session_data:
        for disease, prob in session_data["Predictions"].items():
            data[f"{disease}"] = prob

    df = pd.DataFrame([data])
    csv_file = "user_health_data.csv"
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)


TOKEN = "Your own bot token"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

(
    ASK_NAME, ASK_AGE, ASK_GENDER, ASK_HEIGHT, ASK_WEIGHT,
    ASK_SLEEP, ASK_ACTIVITY, ASK_WATER, ASK_JUNK, ASK_FRUIT,
    ASK_HISTORY, ASK_LIFESTYLE, ASK_LIFESTYLE_FREQ, SHOW_RESULTS
) = range(14)

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hey! I’m HealthMate AI. Let’s take care of your wellness today. What’s your name?")
    return ASK_NAME

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = {'Name': update.message.text}
    await update.message.reply_text(f"Nice to meet you, {update.message.text}! 🎉 How old are you?")
    return ASK_AGE

async def ask_gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Age'] = int(update.message.text)
    reply_keyboard = [['Male', 'Female']]
    await update.message.reply_text("Got it! What’s your gender?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_GENDER

async def ask_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Gender'] = 1 if update.message.text == 'Male' else 0
    await update.message.reply_text("Can you tell me your height in centimeters? 📏")
    return ASK_HEIGHT

async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Height'] = float(update.message.text)
    await update.message.reply_text("Thanks! And your weight in kilograms? ⚖️")
    return ASK_WEIGHT

async def ask_sleep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = user_sessions[update.effective_user.id]
    session['Weight'] = float(update.message.text)
    height_m = session['Height'] / 100
    bmi = round(session['Weight'] / (height_m ** 2), 2)
    session['BMI'] = bmi

    # Send BMI info to user
    bmi_msg = f"📏 Your BMI is **{bmi}**.\n"
    if bmi < 18.5:
        bmi_msg += "🟡 You’re underweight. Consider a balanced diet."
    elif 18.5 <= bmi < 24.9:
        bmi_msg += "🟢 You’re in the healthy range. Great job!"
    elif 25 <= bmi < 29.9:
        bmi_msg += "🟠 You’re overweight. Try to be more active."
    else:
        bmi_msg += "🔴 You’re in the obese range. Let's work on it together!"

    await update.message.reply_text(bmi_msg)
    await update.message.reply_text(f"How many hours of sleep do you get on average per night? 😴")
    return ASK_SLEEP

async def ask_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Sleep_hours'] = float(update.message.text)
    await update.message.reply_text("Awesome! How many minutes do you usually move or exercise daily? 🏃‍♂️")
    return ASK_ACTIVITY

async def ask_water(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Physical_activity_mins'] = float(update.message.text)
    await update.message.reply_text("How many liters of water do you drink every day? 💧")
    return ASK_WATER

async def ask_junk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Water_intake_liters'] = float(update.message.text)
    await update.message.reply_text("How many times a week do you eat junk food like chips, burgers, or soda? 🍔")
    return ASK_JUNK

async def ask_fruit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Junk_food_per_week'] = int(update.message.text)
    await update.message.reply_text("How many servings of fruits and vegetables do you eat per day? 🥗")
    return ASK_FRUIT

async def ask_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Fruit_veggies_per_day'] = int(update.message.text)
    reply_keyboard = [['Yes', 'No']]
    await update.message.reply_text("Do you have a family history of chronic diseases? 🧬",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_HISTORY

async def ask_lifestyle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions[update.effective_user.id]['Family_history'] = 1 if update.message.text == 'Yes' else 0
    reply_keyboard = [['No', 'Smoking', 'Alcohol', 'Both']]
    await update.message.reply_text("Do you smoke or consume alcohol? 🚬🍷",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_LIFESTYLE

async def ask_lifestyle_freq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_sessions[update.effective_user.id]['Lifestyle'] = user_input
    if user_input == ('No','no'):
        user_sessions[update.effective_user.id]['Lifestyle_freq'] = 0
        return await show_results(update, context)
    else:
        await update.message.reply_text("How many times a week do you smoke or drink? 🔁")
        return ASK_LIFESTYLE_FREQ

async def show_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions[user_id]
    if 'Lifestyle_freq' not in session:
        session['Lifestyle_freq'] = int(update.message.text)

    results = predict_health_risks(session)
    session["Predictions"] = {
        disease: {"Label": risk, "Probability": prob}
        for disease, (risk, prob) in results.items()
    }

    # 👇 Save to CSV
    save_user_data_csv(user_id, session)

    dashboard_url = f"https://healthmateai.streamlit.app?user_id={user_id}"

    message = (
        f"✅ Your health checkup is complete!\n"
        f"📊 View your full wellness dashboard & get your 7-day plan here:\n"
        f"👉 {dashboard_url}\n\n"
        f"⏬ You can also download your personalized report from there!"
        )

    await update.message.reply_text(message)


    name = session.get("Name", "Friend")
    result_text = f"📊 Here’s your health checkup summary, {name}:"
    tips = []

    for disease, (risk, prob) in results.items():
        prob_percent = round(prob)
        emoji = "⚠️" if prob_percent >= 20 else "✅"
        result_text += f"\n{emoji} {disease.replace('_', ' ').title()}: {prob_percent}% risk"

        if prob_percent >= 20:
            if disease == "Risk_diabetes":
                tips.append("🍬 Cut back on sugar and walk daily.")
            elif disease == "Risk_anxiety":
                tips.append("🧘 Try meditation and regular sleep.")
            elif disease == "Risk_depression":
                tips.append("📔 Journal your thoughts and talk to someone.")
            elif disease == "Risk_obesity":
                tips.append("🥗 Avoid junk food and move more.")
            elif disease == "Risk_asthma":
                tips.append("😷 Avoid allergens and dusty areas.")
            elif disease == "Risk_migraine":
                tips.append("💡 Reduce screen time and maintain sleep.")
            elif disease == "Risk_tb":
                tips.append("🏥 If coughing persists, get tested.")
            elif disease == "Risk_cancer":
                tips.append("🚭 Avoid smoking/alcohol, eat healthy.")
            elif disease == "Risk_heart_disease":
                tips.append("💓 Eat less salt and fat, stay active.")
            elif disease == "Risk_stress_burnout":
                tips.append("⏳ Take breaks and balance work and rest.")

    await update.message.reply_text(result_text)
    if tips:
        await update.message.reply_text("💡 Health Tips:" + "".join(set(tips)))
    else:
        await update.message.reply_text("✅ You're doing great! Keep up the good habits!")

    context.job_queue.run_repeating(reminder_callback, 7200, first=7200, chat_id=user_id, name=str(user_id))
    await update.message.reply_text("⏰ I’ll remind you every 2 hours with wellness tips to keep you on track! 🌟")
    return ConversationHandler.END

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):
    user_id = int(context.job.name)
    session = user_sessions.get(user_id)
    if not session:
        return

    messages = []
    if session['Water_intake_liters'] < 2:
        messages.append("💧 Stay hydrated! Grab a glass of water.")
    if session['Physical_activity_mins'] < 30:
        messages.append("🏃‍♀️ Time for a quick stretch or walk.")
    if session['Junk_food_per_week'] > 4:
        messages.append("🍏 Choose something fresh and healthy today.")
    if session['Sleep_hours'] < 6:
        messages.append("🛌 Try to get more restful sleep tonight.")

    if messages:
        await context.bot.send_message(chat_id=user_id, text="📣 Friendly Health Reminder:" + "".join(messages))
    else:
        await context.bot.send_message(chat_id=user_id, text="🌟 Keep it up! You’re making awesome progress!")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No worries, your session was cancelled. Type /start to try again. 😊")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gender)],
            ASK_GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_height)],
            ASK_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
            ASK_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_sleep)],
            ASK_SLEEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_activity)],
            ASK_ACTIVITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_water)],
            ASK_WATER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_junk)],
            ASK_JUNK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_fruit)],
            ASK_FRUIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_history)],
            ASK_HISTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_lifestyle)],
            ASK_LIFESTYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_lifestyle_freq)],
            ASK_LIFESTYLE_FREQ: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_results)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    print("🤖 HealthMate AI Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

