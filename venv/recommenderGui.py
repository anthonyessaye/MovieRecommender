from tkinter import *
import recommender
from tkinter import messagebox
import time

# ----------- Declare UI Variables Here --------------------



window = Tk()
 
window.title("Movie Recommender")
window.geometry('1000x700')
window.configure(background="black")

# Name entry text
nameLbl = Label(window, text="Name of movie you like", background="black", fg="white", font="16")
nameLbl.grid(column=1, row=0, padx="50", pady="20")
movie_txt = Entry(window,width=15, font="14")
movie_txt.grid(column=2, row=0)


# Number entry text
numberLbl = Label(window, text="Number of movies to suggest", background="black", fg="white", font="16")
numberLbl.grid(column=1, row=2)
count_txt = Entry(window,width=15, font="14", text="10")
count_txt.grid(column=2, row=2)

#Minimum number of ratings given by users
ratingLbl = Label(window, text="Minimum Rating", background="black", fg="white", font="16")
ratingLbl.grid(column=4, row=0,padx="50")
rating_txt = Entry(window,width=15, font="14")
rating_txt.grid(column=5, row=0)

#Quality of user
userQualityLbl = Label(window, text="User Quality", background="black", fg="white", font="16")
userQualityLbl.grid(column=4, row=2)
quality_txt = Entry(window,width=15, font="14")
quality_txt.grid(column=5, row=2)

# Create a Tkinter variable ---------------
#algoVar = StringVar(window)

#choices = { 'auto', 'ball_tree', 'kd_tree', 'brute'}
#algoVar.set('auto')

#algorithmChosen = OptionMenu(window, algoVar, *choices)
#Label(window, text="Choose an algorithm", background="black", fg="white", font="16").grid(row = 4, column = 1)
#algorithmChosen.grid(row = 4, column =2 ,pady ="20")
#algorithmChosen.config(width= 14, font="14",background = "black", fg="white")
# ------------------------------------------

metricVar = StringVar(window)

metricChoices = {'cityblock', 'cosine', 'euclidean', 'manhattan','minkowski'}
metricVar.set('cosine')

metricChosen = OptionMenu(window, metricVar, *metricChoices)
Label(window, text="Choose a metric", background="black", fg="white", font="16").grid(row = 4, column = 4)
metricChosen.grid(row = 4, column =5)
metricChosen.config(width= 14, font="14",background = "black", fg="white")

# Recommended Label
recommendedLbl = Label(window, text="", background="black", fg="white", font="14")
recommendedLbl.place(relx=0.5, rely=0.5, anchor=CENTER)

# ------------------ Declare all functions below here -------------------

#Function for button click
def onSubmitClicked():
	recommendedLbl.config(text="Loading Suggestions")


	# Pass variables to engine
	recommended = recommender.MyMain(movie_txt.get(), int(count_txt.get()),
									 int(rating_txt.get()),int(quality_txt.get()),metricVar.get())

    #Splitting this maybe later we add a list
	recommendedSplit = recommended.splitlines()

	recommendedLbl.config(text = "Recommended Movies according to what you provided: \n\n" + recommended)



# Submit Button
btn = Button(window, text="Submit", command=onSubmitClicked, width=10, height=2)  # link button command to the function
btn.place(relx=0.5, rely=0.8, anchor=CENTER)

window.mainloop()

