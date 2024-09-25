import json
from tkinter import *
import tkinter as tk
from tkinter import messagebox
from collections import deque
from PIL import Image, ImageTk
import re
from datetime import datetime


# Stack for messages
class MessageStack:
    def _init_(self):
        self.stack = []

    def push(self, message):
        self.stack.append(message)

    def pop(self):
        return self.stack.pop() if self.stack else None

    def get_all_messages(self):
        return self.stack[::-1]  # Latest message first


# Queue for notifications
class NotificationQueue:
    def _init_(self):
        self.queue = deque()

    def enqueue(self, notification):
        self.queue.append(notification)

    def get_all_notifications(self):
        return list(self.queue)


# Post class to handle posts
class Post:
    def _init_(self, content, author):
        self.content = content
        self.author = author
        self.likes = 0
        self.comments = []

    def like_post(self):
        self.likes += 1

    def add_comment(self, comment):
        self.comments.append(comment)


# User class with refactored logic
class User:
    def _init_(self, username, password):
        self.username = username
        self.password = password
        self.posts = []
        self.following = set()
        self.followers = set()
        self.messages = MessageStack()
        self.notifications = NotificationQueue()
        self.friend_requests = set()  # Store incoming friend requests

    def add_post(self, post_content):
        post = Post(post_content, self.username)
        self.posts.append(post)
        self._notify_followers(f"{self.username} posted: {post_content}")

    def delete_post(self, post_index):
        if 0 <= post_index < len(self.posts):
            deleted_post = self.posts.pop(post_index)
            self._notify_followers(f"{self.username} deleted a post: {deleted_post.content}")

    def get_following_posts(self):
        """
        Retrieves the most recent posts from the users that this user follows.
        """
        data = load_data()
        following_posts = []
        for username in self.following:
            user_obj = get_user_from_data(username, data)
            if user_obj:
                for post in user_obj.posts:
                    following_posts.append(f"{post.author}: {post.content} (Likes: {post.likes})")

        return following_posts if following_posts else ["No new posts from followed users"]
    def follow(self, other_user):
        if other_user.username not in self.following:
            self.following.add(other_user.username)
            other_user.followers.add(self.username)
            other_user.notifications.enqueue(f"{self.username} started following you")

    def unfollow(self, other_user):
        if other_user.username in self.following:
            self.following.remove(other_user.username)
            other_user.followers.remove(self.username)
            other_user.notifications.enqueue(f"{self.username} unfollowed you")

    def send_message(self, follower, message_text):
        follower.messages.push(f"{self.username}: {message_text}")
        follower.notifications.enqueue(f"New message from {self.username}")

    def _notify_followers(self, notification_text):
        data = load_data()
        for follower in self.followers:
            follower_obj = get_user_from_data(follower, data)
            if follower_obj:
                follower_obj.notifications.enqueue(notification_text)
        save_data(data)

    def view_messages(self):
        return self.messages.get_all_messages()

    def view_notifications(self):
        return self.notifications.get_all_notifications()

    def send_friend_request(self, target_user):
        """
        Sends a friend request to another user.
        """
        if target_user.username in self.following or target_user.username in self.friend_requests:
            return f"You already follow {target_user.username} or a request is pending."
        target_user.friend_requests.add(self.username)
        save_user(target_user)
        return f"Friend request sent to {target_user.username}."

    def accept_friend_request(self, from_user):
        """
        Accepts a friend request and follows the user.
        """
        if from_user.username in self.friend_requests:
            self.friend_requests.remove(from_user.username)
            self.follow(from_user)
            from_user.follow(self)
            save_user(self)
            save_user(from_user)
            return f"You and {from_user.username} are now friends."
        return f"No friend request from {from_user.username} found."

    def view_friend_requests(self):
        """
        Returns the list of incoming friend requests.
        """
        return list(self.friend_requests) if self.friend_requests else ["No friend requests"]

     # Method to change password
    def change_password(self, new_password):
        self.password = new_password
        save_user(self)
        messagebox.showinfo("Settings", "Password changed successfully!")

    # Method to delete account
    def delete_account(self):
        data = load_data()
        if self.username in data:
            del data[self.username]
            save_data(data)
            messagebox.showinfo("Settings", "Account deleted successfully!")
            login()

# Helper functions to manage data efficiently

def load_data(file_name):
    try:
        with open(file_name, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data, file_name):
    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)

users = load_data('users.json')

def save_user(user_obj):
    data = load_data()
    user_data = {
        "password": user_obj.password,
        "posts": [{"content": p.content, "author": p.author, "likes": p.likes, "comments": p.comments} for p in user_obj.posts],
        "following": list(user_obj.following),
        "followers": list(user_obj.followers),
        "messages": user_obj.messages.stack,
        "notifications": list(user_obj.notifications.queue)
    }
    data["users"][user_obj.username] = user_data
    save_data(data)


def find_user(data, username):
    return data["users"].get(username)


def get_user_from_data(username, data):
    user_data = find_user(data, username)
    if user_data:
        user = User(username, user_data["password"])
        user.posts = [Post(p['content'], p['author']) for p in user_data["posts"]]
        user.following = set(user_data["following"])
        user.followers = set(user_data["followers"])
        user.messages.stack = user_data.get("messages", [])
        user.notifications.queue = deque(user_data.get("notifications", []))
        return user
    return None

def register_user():
    name = reg_entry_name.get()
    phone = reg_entry_phone.get()
    email = reg_entry_username.get()
    password = reg_entry_password.get()
    gender = reg_entry_gender.get()
    day = reg_entry_day.get()
    month = reg_entry_month.get()
    year = reg_entry_year.get()

    if not all([name, phone, email, password, gender, day, month, year]):
        reg_result_label.config(text="All fields are required!", fg="red")
        return

    if not (phone.isdigit()):
        reg_result_label.config(text="Phone number must be numeric!", fg="red")
        return

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        reg_result_label.config(text="Invalid email format!", fg="red")
        return

    try:
        birth_date = datetime(int(year), int(month), int(day))
        age = (datetime.now() - birth_date).days // 365
        if age < 16:
            reg_result_label.config(text="You must be at least 16 years old to register.", fg="red")
            return
    except ValueError:
        reg_result_label.config(text="Invalid birth date!", fg="red")
        return

    if email in users:
        reg_result_label.config(text="User already exists!", fg="red")
        return

    new_user = {
        'name': name,
        'phone': phone,
        'email': email,
        'password': password,
        'gender': gender,
        'birth_date': birth_date.strftime("%Y-%m-%d"),
    }

    users[email] = new_user
    save_data(users, 'users.json')
    reg_result_label.config(text="Registration successful!", fg="green")


def open_register_window():
    window.withdraw()
    register_window = tk.Toplevel(window)
    register_window.title("Sign up")
    register_window.geometry("400x600")
    register_window.configure(bg='#f0f2f5')

    logo_label = tk.Label(register_window, image=resized_logo, bg='#f0f2f5')
    logo_label.place(x=10, y=10)

    tk.Label(register_window, text="Sign Up", font=('Arial', 20), bg='#f0f2f5').pack(pady=10)

    tk.Label(register_window, text="Name:", font=('Arial', 12), bg='#f0f2f5').pack(pady=5)
    global reg_entry_name
    reg_entry_name = tk.Entry(register_window)
    reg_entry_name.pack(pady=5)

    tk.Label(register_window, text="Phone:", font=('Arial', 12), bg='#f0f2f5').pack(pady=5)
    global reg_entry_phone
    reg_entry_phone = tk.Entry(register_window)
    reg_entry_phone.pack(pady=5)

    tk.Label(register_window, text="Email:", font=('Arial', 12), bg='#f0f2f5').pack(pady=5)
    global reg_entry_username
    reg_entry_username = tk.Entry(register_window)
    reg_entry_username.pack(pady=5)

    tk.Label(register_window, text="Password:", font=('Arial', 12), bg='#f0f2f5').pack(pady=5)
    global reg_entry_password
    reg_entry_password = tk.Entry(register_window, show="*")
    reg_entry_password.pack(pady=5)

    tk.Label(register_window, text="Birth-Date:", font=('Arial', 12), bg='#f0f2f5').pack(pady=5)

    frame_date = tk.Frame(register_window, bg='#f0f2f5')
    frame_date.pack(pady=5)

    global reg_entry_day, reg_entry_month, reg_entry_year
    reg_entry_day = tk.Entry(frame_date, width=5)
    reg_entry_month = tk.Entry(frame_date, width=5)
    reg_entry_year = tk.Entry(frame_date, width=7)

    reg_entry_day.pack(side=tk.LEFT, padx=5)
    tk.Label(frame_date, text="Day", bg='#f0f2f5').pack(side=tk.LEFT)
    reg_entry_month.pack(side=tk.LEFT, padx=5)
    tk.Label(frame_date, text="Month", bg='#f0f2f5').pack(side=tk.LEFT)
    reg_entry_year.pack(side=tk.LEFT, padx=5)
    tk.Label(frame_date, text="Year", bg='#f0f2f5').pack(side=tk.LEFT)


    tk.Label(register_window, text="Gender:", font=('Arial', 12), bg='#f0f2f5').pack(pady=10)
    global reg_entry_gender
    reg_entry_gender = tk.StringVar(value="Male")
    gender_frame = tk.Frame(register_window, bg='#f0f2f5')
    gender_frame.pack()

    tk.Radiobutton(gender_frame, text="Male", variable=reg_entry_gender, value="Male", bg='#f0f2f5').pack(side=tk.LEFT, padx=20)
    tk.Radiobutton(gender_frame, text="Female", variable=reg_entry_gender, value="Female", bg='#f0f2f5').pack(side=tk.LEFT, padx=20)

    tk.Button(register_window, text="Sign up", command=register_user, bg='green', fg='white').pack(pady=10)
    tk.Button(register_window, text="Back", command=lambda: back_to_login(register_window), bg='#4267B2', fg='white').pack(pady=10)

    global reg_result_label
    reg_result_label = tk.Label(register_window, text="", font=('Arial', 12), bg='#f0f2f5')
    reg_result_label.pack(pady=10)

def back_to_login(register_window):
    register_window.destroy()
    window.deiconify()

def login():
    email = entry.get()
    password = entry2.get()

    if email in users and users[email]['password'] == password:
        open_user_dashboard(users[email]['name'])
        window.withdraw()
    else:
        result_label.config(text="Login Failed. Invalid Username or Password.", fg="red")


def confirm_logout(current_window):
    confirm_window = tk.Toplevel(window)
    confirm_window.title("Confirm Logout")
    confirm_window.geometry("300x150")
    confirm_window.configure(bg='#f0f2f5')

    message_label = tk.Label(confirm_window, text="Logout of your account?", bg='#f0f2f5', font=('Arial', 14))
    message_label.pack(pady=20)
    logout_button = tk.Button(confirm_window, text="Logout",
                              command=lambda: logout_and_close(current_window, confirm_window), bg='red', fg='white')
    logout_button.pack(side=tk.LEFT, padx=20, pady=10)

    cancel_button = tk.Button(confirm_window, text="Cancel", command=confirm_window.destroy, bg='black', fg='white')
    cancel_button.pack(side=tk.RIGHT, padx=20, pady=10)


def logout_and_close(current_window, confirm_window):
    entry.delete(0, tk.END)
    entry2.delete(0, tk.END)

    current_window.destroy()
    confirm_window.destroy()
    window.deiconify()


def open_user_dashboard(name):
    user_window = tk.Toplevel(window)
    user_window.title("User Dashboard")
    user_window.geometry("400x400")
    user_window.configure(bg='#f0f2f5')

    tk.Label(user_window, text=f"Welcome {name}!", font=("Arial", 18), bg='#f0f2f5').pack(pady=10)
    tk.Button(user_window, text="Logout", command=lambda: confirm_logout(user_window), bg='#4267B2', fg='white').pack(
        pady=10)


def on_button_click(event):
    event.widget.config(bg='#3b5998')

def on_button_release(event):
    event.widget.config(bg='#4267B2')

window = tk.Tk()
window.title("FaceBook Application")
window.geometry("400x400")
window.configure(bg='#f0f2f5')

original_logo = Image.open("facebook-logo-icon.png")
resized_logo = ImageTk.PhotoImage(original_logo.resize((50, 50), Image.LANCZOS))

logo_label = tk.Label(window, image=resized_logo, bg='#f0f2f5')
logo_label.place(x=10, y=10)

tk.Label(window, text="Login", font=('Arial', 20), bg='#f0f2f5').pack(pady=10)
tk.Label(window, text="Email:", font=('Arial', 14), bg='#f0f2f5').pack(pady=5)
entry = tk.Entry(window)
entry.pack(pady=5)

tk.Label(window, text="Password:", font=('Arial', 14), bg='#f0f2f5').pack(pady=5)
entry2 = tk.Entry(window, show="*")
entry2.pack(pady=5)

result_label = tk.Label(window, text="", font=('Arial', 12), bg='#f0f2f5')
result_label.pack(pady=10)

login_button = tk.Button(window, text="Login", command=login, bg='#4267B2', fg='white')
login_button.pack(pady=10)
login_button.bind("<ButtonPress>", on_button_click)
login_button.bind("<ButtonRelease>", on_button_release)

register_button = tk.Button(window, text="Create new account", command=open_register_window, bg='green', fg='white')
register_button.pack(pady=10)
register_button.bind("<ButtonPress>", on_button_click)
register_button.bind("<ButtonRelease>", on_button_release)

window.mainloop()

# Settings Menu (new feature)
def settings_menu(user):
    def change_password():
        new_password = entry_new_password.get()
        if new_password:
            user.change_password(new_password)
            root.destroy()
        else:
            messagebox.showerror("Error", "New password cannot be empty")

    def delete_account():
        confirm = messagebox.askyesno("Delete Account", "Are you sure you want to delete your account?")
        if confirm:
            user.delete_account()
            root.destroy()

    # Settings GUI layout
    root = Tk()
    root.title("Settings")

    Label(root, text="Change Password").grid(row=0, column=0)
    entry_new_password = Entry(root, show="*")
    entry_new_password.grid(row=0, column=1)
    Button(root, text="Change", command=change_password).grid(row=0, column=2)

    Button(root, text="Delete Account", command=delete_account, fg="red").grid(row=1, column=1)

    root.mainloop()

def main_menu(user):
    def create_post():
        content = entry_post.get()
        if content:
            user.add_post(content)
            save_user(user)
            messagebox.showinfo("Post", "Post created!")
        else:
            messagebox.showerror("Error", "Post content cannot be empty")

    def delete_post():
        post_index = int(entry_post_index.get()) - 1
        if 0 <= post_index < len(user.posts):
            user.delete_post(post_index)
            save_user(user)
            messagebox.showinfo("Delete Post", "Post deleted!")
        else:
            messagebox.showerror("Error", "Invalid post index")


    def view_following_posts():
        posts = user.get_following_posts()
        messagebox.showinfo("Following Posts", "\n".join(posts))

    def follow_user():
        target_user = entry_follow.get()
        data = load_data()
        target_user_obj = get_user_from_data(target_user, data)
        if target_user_obj:
            user.follow(target_user_obj)
            save_user(user)
            save_user(target_user_obj)
            messagebox.showinfo("Follow", f"You are now following {target_user}")
        else:
            messagebox.showerror("Follow", "User not found")

    def unfollow_user():
        target_user = entry_follow.get()
        data = load_data()
        target_user_obj = get_user_from_data(target_user, data)
        if target_user_obj:
            user.unfollow(target_user_obj)
            save_user(user)
            save_user(target_user_obj)
            messagebox.showinfo("Unfollow", f"You unfollowed {target_user}")
        else:
            messagebox.showerror("Unfollow", "User not found")

    def send_message():
        follower = entry_follower.get()
        message = entry_message.get()
        data = load_data()
        follower_obj = get_user_from_data(follower, data)
        if follower_obj and follower in user.followers:
            user.send_message(follower_obj, message)
            save_user(follower_obj)
            messagebox.showinfo("Message", "Message sent!")
        else:
            messagebox.showerror("Message", "User not found or not a follower")

    def view_messages():
        messages = user.view_messages()
        messagebox.showinfo("Messages", "\n".join(messages) if messages else "No messages")

    def view_notifications():
        notifications = user.view_notifications()
        messagebox.showinfo("Notifications", "\n".join(notifications) if notifications else "No notifications")

    def send_friend_request():
        target_user = entry_friend_request.get()
        data = load_data()
        target_user_obj = get_user_from_data(target_user, data)
        if target_user_obj:
            message = user.send_friend_request(target_user_obj)
            save_user(user)
            save_user(target_user_obj)
            messagebox.showinfo("Friend Request", message)
        else:
            messagebox.showerror("Error", "User not found")

    def accept_friend_request():
        request_from = entry_accept_request.get()
        data = load_data()
        from_user_obj = get_user_from_data(request_from, data)
        if from_user_obj:
            message = user.accept_friend_request(from_user_obj)
            save_user(user)
            save_user(from_user_obj)
            messagebox.showinfo("Friend Request", message)
        else:
            messagebox.showerror("Error", "User not found")

    def view_friend_requests():
        requests = user.view_friend_requests()
        messagebox.showinfo("Friend Requests", "\n".join(requests))


    # GUI layout for main menu
    root = Tk()
    root.title(f"Welcome, {user.username}")

    Label(root, text="Create Post").grid(row=0, column=0)
    entry_post = Entry(root)
    entry_post.grid(row=0, column=1)
    Button(root, text="Post", command=create_post).grid(row=0, column=2)

    Label(root, text="Delete Post (index)").grid(row=1, column=0)
    entry_post_index = Entry(root)
    entry_post_index.grid(row=1, column=1)
    Button(root, text="Delete", command=delete_post).grid(row=1, column=2)

    # Button for viewing posts from users you follow
    Button(root, text="View Friends' Posts", command=view_following_posts).grid(row=5, column=0)

    Label(root, text="Follow/Unfollow User").grid(row=2, column=0)
    entry_follow = Entry(root)
    entry_follow.grid(row=2, column=1)
    Button(root, text="Follow", command=follow_user).grid(row=2, column=2)
    Button(root, text="Unfollow", command=unfollow_user).grid(row=2, column=3)

    Label(root, text="Send Message to Follower").grid(row=3, column=0)
    entry_follower = Entry(root)
    entry_follower.grid(row=3, column=1)
    entry_message = Entry(root)
    entry_message.grid(row=3, column=2)
    Button(root, text="Send", command=send_message).grid(row=3, column=3)

    Button(root, text="View Messages", command=view_messages).grid(row=4, column=0)
    Button(root, text="View Notifications", command=view_notifications).grid(row=4, column=1)

       # New buttons for friend requests
    Label(root, text="Send Friend Request").grid(row=5, column=0)
    entry_friend_request = Entry(root)
    entry_friend_request.grid(row=5, column=1)
    Button(root, text="Send Request", command=send_friend_request).grid(row=5, column=2)

    Label(root, text="Accept Friend Request").grid(row=6, column=0)
    entry_accept_request = Entry(root)
    entry_accept_request.grid(row=6, column=1)
    Button(root, text="Accept Request", command=accept_friend_request).grid(row=6, column=2)

    Button(root, text="View Friend Requests", command=view_friend_requests).grid(row=7, column=0)
       # New buttons for friend requests
    Label(root, text="Send Friend Request").grid(row=5, column=0)
    entry_friend_request = Entry(root)
    entry_friend_request.grid(row=5, column=1)
    Button(root, text="Send Request", command=send_friend_request).grid(row=5, column=2)

    Label(root, text="Accept Friend Request").grid(row=6, column=0)
    entry_accept_request = Entry(root)
    entry_accept_request.grid(row=6, column=1)
    Button(root, text="Accept Request", command=accept_friend_request).grid(row=6, column=2)

    Button(root, text="View Friend Requests", command=view_friend_requests).grid(row=7, column=0)


    root.mainloop()



