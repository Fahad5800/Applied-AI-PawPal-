# PawPal+ Project Reflection

## 1. System Design
- Allow user to input basic pet infromation and their availability. Pet specificities can include(type, age, and any special need).
- Allow users to edit, add, or remove pet tasks.
- Generate a daily customizable pet plan that can be changed based on time availability, priorities, and owner preferences. 
- To develop the system, I think we need pet, owner, task, and manager (does scheduling) class
**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

---
Response: 
- I chose 4 classes for this project - Pet, Tasks, Schedular, and Owner. Pet and Owner classes represents original owner and an animal in real life. While Task represent the entity of task itself. Schedular is like a manager who allows owner/user to change or edit the schedule. 
- Pet class have name, species, age, and any special needs. Task stores timing, frequency, and priority of the owner. Owner hold's its properties such as name, availability, and preferences to build a plan. Schedular connects all the other classes, pet, tasks, and owner, and is responsible for producing a schedule.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---
Response:
- Owner has no Pet or Task collection: The owner class is not connected with pet and tasks. This makes owner unaware of his pet or tasks in the app.
- Schedular only supports a single pet, in real system, we will be having multiple pets
- Task does not contain any id attribute
- 

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---
Response:
- The scheduler uses a greedy approach: it sorts tasks by priority (highest first), then by duration (longest first), then by pet name, and assigns each task to the earliest available time slot that fits. This can lead to suboptimal schedules where a long, lower-priority task blocks time that could have been used for multiple shorter, higher-priority tasks later in the day.
- This tradeoff is reasonable for this scenario because it provides a simple, predictable scheduling algorithm that is easy to understand and implement, prioritizing urgent tasks first. For a pet care app with typically short tasks and limited owner availability, the greedy method usually produces acceptable results without the complexity of more advanced optimization algorithms like bin packing or constraint satisfaction.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
