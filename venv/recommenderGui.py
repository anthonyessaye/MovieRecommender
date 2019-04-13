from tkinter import *
import recommender
from tkinter import messagebox

# ----------- Declare UI Variables Here --------------------

window = Tk()
 
window.title("Movie Recommender")
window.geometry('800x600')
window.configure(background="black")

# Name entry text
nameLbl = Label(window, text="Name of movie you like", background="black", fg="white", font="16")
nameLbl.grid(column=1, row=0)
movie_txt = Entry(window,width=15, font="14")
movie_txt.grid(column=2, row=0)


# Number entry text
numberLbl = Label(window, text="Number of movies to suggest", background="black", fg="white", font="16")
numberLbl.grid(column=1, row=2)
count_txt = Entry(window,width=15, font="14")
count_txt.grid(column=2, row=2)

# Recommended Label
recommendedLbl = Label(window, text="", background="black", fg="white", font="14")
recommendedLbl.place(relx=0.5, rely=0.35, anchor=CENTER)

# ------------------ Declare all functions below here -------------------

#Function for button click
def onSubmitClicked():
	# Pass variables to engine
	recommended = recommender.MyMain(movie_txt.get(), int(count_txt.get()))

    #Splitting this maybe later we add a list
	recommendedSplit = recommended.splitlines()

	recommendedLbl.config(text = "Recommended Movies according to what you provided: \n\n" + recommended)



# Submit Button
btn = Button(window, text="Submit", command=onSubmitClicked, width=10, height=2)  # link button command to the function
btn.place(relx=0.5, rely=0.8, anchor=CENTER)

window.mainloop()