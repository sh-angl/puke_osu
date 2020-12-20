from tkinter import *
from playsound import playsound
import time
"""
This game is very similar to the popular game Osu! It is a rhythm game, where after you choose the level at the top 
(2 included, What is Love by TWICE and Make a Move by Icon for Hire), you attempt to click the circles that appear 
on screen in time to the beat of the song. The correct time to click them is shown by when the circle of decreasing 
size is close to size of the solid circle. The closer you get, the more points you earn. You also earn more points 
the closer you are to the correct time. The songs and the levels were made for the game Osu! and parts have been 
used for the game I have made. The source for this can be found in comments in the python file. To run this you 
need the 'playsound' python package which can be gotten from pip using 'pip install playsound' or there will be no 
audio for the game. All files should be placed in the same folder for the game to work. More levels can be 
downloaded from osu.ppy.sh with a little modification of the script main.py given.
"""




class HitObject:
    def __init__(self, x, y, time):
        self.x = x
        self. y = y
        self.time = time
        self.decreasing_circle = None
        self.circle = None

        # state will contain an int representing the different states, i will decide the states later
        """
            0 = not displayed yet
            1 = displayed
        """
        self.state = 0


        self.size = 60

    def animate(self, canvas, now):
        self.circleAnimation(canvas, now)



    def circleAnimation(self, canvas, now):
        # print(self.circle)
        canvas.delete(self.decreasing_circle)

        time_offset = self.time/1000 - now
        radius = self.size + (100 * (time_offset))

        self.decreasing_circle = canvas.create_oval(self.x - radius, self.y - radius, self.x + radius, self.y + radius, outline="blue")

    def draw(self, canvas):
        radius = self.size
        self.circle = canvas.create_oval(self.x - radius, self.y - radius, self.x + radius, self.y + radius, fill="blue")
        self.state = 1
        # print(self.circle)

    def end_gfx(self, canvas):
        # print("end_gfx", self.circle)
        # print(self.decreasing_circle)
        canvas.delete(self.circle)
        canvas.delete(self.decreasing_circle)

    def click(self, event):
        """
            none if it cannot process hit (e.g. not displayed yet),False if it missed or a number if it returns a score
        """
        now = time.time() * 1000
        if self.time - now > 1000: 
            return None
        if distance(self.x, event.x, self.y, event.y) > self.size:
            return False
        elif self.time - now > 500:
            return 50
        elif self.time - now > 200:
            return 100
        else: 
            return 200

# More work needs to be done on these other hit_object type before they can be used , but most importatntly needed is a different audio 'engine'

class Slider(HitObject):
    def __init__(self, x, y, time, extra_points):
        HitObject.__init__(self,x,y,time,)
        self.extra_points = extra_points
        self.extra_circles = []
        print(self.extra_points)

    def draw(self, canvas):
        radius = self.size
        self.circle = canvas.create_oval(self.x - radius, self.y - radius, self.x + radius, self.y + radius, fill="red")
        self.state = 1
        # print(self.circle)

    def circleAnimation(self, canvas, now):
        # print(self.circle)
        canvas.delete(self.decreasing_circle)

        time_offset = self.time/1000 - now
        radius = self.size + (100 * (time_offset))

        self.decreasing_circle = canvas.create_oval(self.x - radius, self.y - radius, self.x + radius, self.y + radius, outline="red")

    def end_gfx(self, canvas):
        print("end_gfx", self.circle)
        # print(self.decreasing_circle)
        canvas.delete(self.circle)
        canvas.delete(self.decreasing_circle)
        for ele in self.extra_circles:
            canvas.delete(ele)


class LinearSlider(Slider):
    def __init__(self,x, y, time, extrathingies):
        # print(extrathingies)
        Slider.__init__(self, x, y, time, extrathingies)
        pass

    def draw(self, canvas):
        radius = self.size
        self.circle = canvas.create_oval(self.x - radius, self.y - radius, self.x + radius, self.y + radius, outline="red")
        for elem in self.extra_points:
            self.extra_circles.append(canvas.create_oval(elem.x-radius, elem.y - radius, elem.x + radius, elem.y + radius, outline="red"))

class XandY:
    def __init__(self, x, y):
        self.x = x
        self.y = y    

class Game:
    def __init__(self, canvas):
        self.level = ""

        self.canvas = canvas


        self.hit_object_array = []
        self.length = 0

        self.start_draw_pointer = 0
        self.on_time_pointer = 0

        self.anim_lower = 0
        self.anim_higher = 0

        self.start_time = 0

        self.score = 0
        self.combo = 0
        self.multiplier = 1

        self.combo_id = None
        self.score_id = None


        self.mouse_press = False


    def buttonPress1(self, event):
        self.button1 = True
        # print(event.x, event.y)
        if self.on_time_pointer >= self.length:
            return
        maybe_hit = self.hit_object_array[self.on_time_pointer].click(event)

        if maybe_hit == None:
            # print("too early")
            pass
        elif maybe_hit == False:
            self.hit_object_array[self.on_time_pointer].end_gfx(self.canvas)
            self.on_time_pointer += 1
            self.combo = 0
            self.multiplier = 1
            self.update_score()
        else:
            playsound("drum-hitnormal.wav", False)
            self.hit_object_array[self.on_time_pointer].end_gfx(self.canvas)
            self.on_time_pointer += 1
            self.combo += 1
            self.score += maybe_hit * self.multiplier
            self.multiplier = self.multiplier * 1.01
            self.update_score()


    def update_score(self):
        self.canvas.delete(self.combo_id)
        self.canvas.delete(self.score_id)
        self.score_id = self.canvas.create_text(1150, 40, text="Score: " + str(int(self.score)), font=('Helvetica', '20'))
        self.combo_id = self.canvas.create_text(1150, 80, text="Combo: " + str(self.combo), font=('Helvetica', '20'))




    def buttonRelease1(self, event):
        # self.button1 = False
        # print("yo")
        pass

    def makeTrack(self, path):

        self.level = path

        with open(path + ".osu",encoding="utf-8") as file:
            string = file.read()
            start = string.index("[HitObjects]")
            hit_objects = string[start + 1:]
            try:
                a = hit_objects.index("[")
                hit_objects = hit_objects[:a]
            except ValueError:
                pass
            hit_objects = hit_objects + " "
            hit_objects = hit_objects.split("\n")
            hit_objects = hit_objects[1:-1]
            # print(hit_objects)
            for each in hit_objects:
                each = each.split(",")
                # print(int(each[2]))
                obj_type = int(each[3])

                #the specs specify bits so must control on bits
                if True:#obj_type & 1 != 0:
                    self.hit_object_array.append(HitObject(int(each[0]) * 2, int(each[1]) * 2, int(each[2])))
                    # print("simple")
                elif obj_type & 2 != 1:
                    #slider
                    # print("slider")
                    slider_stuff = each[5]
                    slider_type = slider_stuff[0]
                    print(slider_stuff)
                    if slider_type == "L":
                        print("linear")
                        extra_points = slider_stuff.split("|")
                        pass_it_on = []
                        if len(extra_points) >= 1:
                            for elem in extra_points[1:]:
                                thing = elem.split(":")
                                pass_it_on.append(XandY(int(thing[0]) * 2, int(thing[1]) * 2))

                        self.hit_object_array.append(LinearSlider(int(each[0]) * 2, int(each[1]) * 2, int(each[2]), pass_it_on))
                    else:
                        #ther are other slider types which i dont have time to implement
                        self.hit_object_array.append(HitObject(int(each[0]) * 2, int(each[1]) * 2, int(each[2])))
                    
                elif obj_type & 8 != 0:
                    #its a spinner probably wont implement
                    pass
                
            
            # print(self.hit_object_array)
            self.length = len(self.hit_object_array)

    def start_map(self):
        # print("start_map")
        playsound(self.level + ".mp3", False)
        self.start_time = time.time()
        self.tick()
        self.update_score()
       


    def tick(self):
        now = time.time() - self.start_time



        while self.start_draw_pointer < self.length and (now * 1000)> self.hit_object_array[self.start_draw_pointer].time - 1000:
            curr_circle = self.hit_object_array[self.start_draw_pointer]
            curr_circle.draw(self.canvas)
            

            self.start_draw_pointer += 1

        
        for circle in self.hit_object_array[self.on_time_pointer: self.start_draw_pointer]:
           circle.animate(self.canvas,now)

        while self.on_time_pointer < self.length and (now * 1000)> self.hit_object_array[self.on_time_pointer].time + 150:
            curr_circle = self.hit_object_array[self.on_time_pointer]
            # print(self.hit_object_array[self.on_time_pointer].circle)
            """
                guess what, I would love to call this function and have it work but for some reason python is inling values or it is thinking the pointer never got updated due to some concurrency weird model that tkinter after has or python is bugged.
            """

            curr_circle.end_gfx(self.canvas)
            # playsound("./baseAssests/drum-hitnormal.wav", False)
            self.on_time_pointer += 1

        # print(self.hit_object_array[0].circle)

        # while (now * 1000)> self.hit_object_array[self.center_bound].time:
        #     self.anim_lower += 1
        
        # print("frame")




        self.canvas.after(17, self.tick)


 

def distance (x1, x2, y1, y2):
    return ((x1-x2)**2 + (y1 - y2)**2)**(1/2)

    




root = Tk()





# print(hit_object_array)

# def simple_func(track):
#     # canvas.delete("all")
#     # canvas.create_oval(0, 0, 100, 100, fill="blue")
#     now = time.time()
#     # print(track.hit_object_array[track.next_hit].time, (now - track.start_offset) * 1000)
#     # print(track.hit_object_array[track.next_hit].time)
#     if track.hit_object_array[track.next_hit].time < (now - track.start_offset) * 1000:
#         curr_circle = track.hit_object_array[track.next_hit]
#         track.next_hit += 1
#         print("next circle")
#         canvas.create_oval(curr_circle.x -50, curr_circle.y -50, curr_circle.x +50, curr_circle.y +50, fill="blue")
#         playsound("./baseAssests/drum-hitnormal.wav", False)

#     canvas.after(17, simple_func, track)

# canvas.create_oval(0, 0, 100, 100, fill="blue")
# playsound("./songs/765778 Icon For Hire - Make a Move (Speed Up Ver)/audio.mp3", False)


def init_controls(game):
    # print("initing controls")
    root.bind("<ButtonRelease 1>",game.buttonRelease1)
    root.bind("<ButtonPress 1>",game.buttonPress1)





class Menu:
    def __init__(self, canvas):
        self.canvas = canvas

    def what_is_love(self):
        #This one is the easiest level from this link https://osu.ppy.sh/beatmapsets/762823#osu/1603791
        self.canvas.pack_forget()
        
        self.canvas = Canvas(root, width=1280, height=960, background="grey")
        self.canvas.pack()



        first = Game(self.canvas)

        first.makeTrack("./what_is_love")
        init_controls(first)

        first.start_map()


    def make_a_move(self):
        #This one is the easiest level from this link https://osu.ppy.sh/beatmapsets/765778#osu/1627148
        self.canvas.pack_forget()
        
        self.canvas = Canvas(root, width=1280, height=960, background="grey")
        self.canvas.pack()



        first = Game(self.canvas)

        first.makeTrack("./make_a_move")
        init_controls(first)

        first.start_map()

men_frame = Frame(root)

canvas = Canvas(root, width=1280, height=960, background="grey")   
unused = Menu(canvas)


label = Label(men_frame, text="Choose a level:")
label.grid(row=0, column=0)

button_a = Button(men_frame, text="What is Love - TWICE", command=unused.what_is_love)
button_a.grid(row=0, column=1)

button_b = Button(men_frame, text="Make a Move", command=unused.make_a_move)
button_b.grid(row=0, column=2)

men_frame.pack()


canvas.pack()









root.mainloop()