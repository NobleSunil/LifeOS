import os
import django
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

# Model imports
from lifeos_app.models import Goal, Task, Habit, HabitCompletion, UserProfile

class Command(BaseCommand):
    help = 'Seeds the database with LifeOS demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting demo data seed...')

        with transaction.atomic():
            # STEP 1 — CREATE 28 USERS
            users_data = [
                ("arjun_menon", "arjun.menon@gmail.com", "Demo@1234", 28),
                ("priya_nair", "priya.nair@outlook.com", "Demo@1234", 21),
                ("rohan_das", "rohan.das@yahoo.com", "Demo@1234", 26),
                ("sneha_pillai", "sneha.pillai@gmail.com", "Demo@1234", 29),
                ("karthik_iyer", "karthik.iyer@hotmail.com", "Demo@1234", 24),
                ("divya_krishna", "divya.krishna@gmail.com", "Demo@1234", 27),
                ("arun_thomas", "arun.thomas@protonmail.com", "Demo@1234", 31),
                ("meera_varma", "meera.varma@gmail.com", "Demo@1234", 34),
                ("vikram_shetty", "vikram.shetty@outlook.com", "Demo@1234", 32),
                ("ananya_reddy", "ananya.reddy@gmail.com", "Demo@1234", 23),
                ("siddharth_joshi", "siddharth.joshi@gmail.com", "Demo@1234", 25),
                ("kavya_menon", "kavya.menon@yahoo.com", "Demo@1234", 26),
                ("nikhil_sharma", "nikhil.sharma@gmail.com", "Demo@1234", 35),
                ("pooja_iyer", "pooja.iyer@outlook.com", "Demo@1234", 28),
                ("rahul_nambiar", "rahul.nambiar@gmail.com", "Demo@1234", 20),
                ("shreya_bose", "shreya.bose@gmail.com", "Demo@1234", 24),
                ("aditya_mehta", "aditya.mehta@protonmail.com", "Demo@1234", 27),
                ("lakshmi_pillai", "lakshmi.pillai@gmail.com", "Demo@1234", 30),
                ("vishnu_kumar", "vishnu.kumar@hotmail.com", "Demo@1234", 29),
                ("neethu_suresh", "neethu.suresh@gmail.com", "Demo@1234", 22),
                ("gautam_pandey", "gautam.pandey@outlook.com", "Demo@1234", 33),
                ("ishaan_chandra", "ishaan.chandra@gmail.com", "Demo@1234", 16),
                ("roshni_alex", "roshni.alex@gmail.com", "Demo@1234", 29),
                ("deepak_nair", "deepak.nair@yahoo.com", "Demo@1234", 25),
                ("anjali_das", "anjali.das@gmail.com", "Demo@1234", 27),
                ("sundar_raj", "sundar.raj@outlook.com", "Demo@1234", 31),
                ("tejal_shah", "tejal.shah@gmail.com", "Demo@1234", 28),
                ("bharath_menon", "bharath.menon@protonmail.com", "Demo@1234", 42),
            ]

            users = {}
            for username, email, password, age in users_data:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(username=username, email=email, password=password)
                else:
                    user = User.objects.get(username=username)
                    
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.age = age
                profile.save()
                users[username] = user

            today = date.today()
            def past(n): return today - timedelta(days=n)
            def future(n): return today + timedelta(days=n)

            # STEP 2 & 3 — CREATE GOALS AND TASKS PER USER
            goals_data = {
                "arjun_menon": [
                    ("Get AWS Solutions Architect Certified", future(60), False),
                    ("Run a 10K under 55 minutes", future(45), False),
                    ("Save ₹1,00,000 by year end", future(180), False),
                    ("Read 12 books this year", future(270), True),
                ],
                "priya_nair": [
                    ("Score 85%+ in semester exams", future(30), False),
                    ("Learn basic Python programming", future(60), False),
                    ("Build a personal portfolio website", future(90), False),
                ],
                "rohan_das": [
                    ("Land 3 new freelance clients", future(45), False),
                    ("Learn UI/UX fundamentals", future(75), False),
                    ("Reduce screen time to under 3 hrs/day", future(30), True),
                    ("Complete React JS crash course", past(10), True),
                ],
                "sneha_pillai": [
                    ("Lose 8 kg in 3 months", future(90), False),
                    ("Complete 30-day yoga challenge", future(25), False),
                    ("Drink 3L water daily for 60 days", future(55), False),
                    ("Run a half marathon", future(120), False),
                    ("Eliminate junk food for 30 days", past(5), True),
                ],
                "karthik_iyer": [
                    ("Crack CAT 2025 with 95 percentile", future(60), False),
                    ("Complete financial modeling course", future(40), False),
                    ("Network with 20 industry professionals", future(90), False),
                    ("Write a business plan for mock startup", future(30), False),
                ],
                "divya_krishna": [
                    ("Build a full UX case study portfolio", future(75), False),
                    ("Master Figma advanced prototyping", future(45), True),
                    ("Get a UX job at a product company", future(120), False),
                ],
                "arun_thomas": [
                    ("Complete SQL mastery course", past(15), True),
                    ("Build 3 end-to-end data dashboards", future(60), False),
                    ("Learn Python pandas and matplotlib", future(30), False),
                    ("Get Power BI certification", future(90), False),
                ],
                "meera_varma": [
                    ("Read 20 books this year", future(200), False),
                    ("Learn digital tools for classroom", future(60), False),
                    ("Meditate daily for 90 days", future(80), False),
                ],
                "vikram_shetty": [
                    ("Launch MVP of SaaS product", future(90), False),
                    ("Raise pre-seed funding of ₹25 lakhs", future(180), False),
                    ("Hire first 3 team members", future(60), False),
                    ("Reach 500 beta signups", future(75), False),
                    ("Complete YC startup school", future(30), True),
                ],
                "ananya_reddy": [
                    ("Clear USMLE Step 1", future(120), False),
                    ("Complete anatomy revision", future(20), False),
                    ("Improve sleep to 7 hrs/night", future(60), False),
                ],
                "siddharth_joshi": [
                    ("Master Django REST Framework", future(45), False),
                    ("Contribute to 5 open source projects", future(90), False),
                    ("Build and deploy a SaaS side project", future(120), False),
                    ("Get Docker and Kubernetes certified", future(75), False),
                ],
                "kavya_menon": [
                    ("Grow LinkedIn to 2000 followers", future(90), False),
                    ("Publish 30 blogs in 3 months", future(90), False),
                    ("Complete copywriting course", past(20), False),
                ],
                "nikhil_sharma": [
                    ("Get PSPO certification", future(45), False),
                    ("Launch 2 product features this quarter", future(30), False),
                    ("Build a product roadmap for a real app", past(5), True),
                    ("Read 'Inspired' by Marty Cagan", past(30), True),
                ],
                "pooja_iyer": [
                    ("Complete HR analytics certification", future(60), False),
                    ("Improve public speaking skills", future(90), False),
                    ("Practice journaling for 60 days", future(50), False),
                ],
                "rahul_nambiar": [
                    ("Clear all 6 semester subjects", future(45), False),
                    ("Build an IoT project for final year", future(100), False),
                    ("Learn C++ for competitive programming", future(60), False),
                    ("Get an internship at a core company", future(90), False),
                ],
                "shreya_bose": [
                    ("Build a Behance portfolio with 10 projects", future(80), False),
                    ("Learn motion graphics in After Effects", future(60), False),
                    ("Freelance and earn ₹20,000/month", future(90), False),
                ],
                "aditya_mehta": [
                    ("Learn advanced Excel and VBA", past(10), True),
                    ("Build investment portfolio tracker", future(30), False),
                    ("Complete CFA Level 1 prep", future(150), False),
                    ("Save 30% of income monthly", future(180), False),
                ],
                "lakshmi_pillai": [
                    ("Complete BSc nursing post-basic course", future(120), False),
                    ("Exercise 4 times per week for 60 days", future(55), False),
                    ("Reduce caffeine intake", future(30), True),
                ],
                "vishnu_kumar": [
                    ("Get CKA Kubernetes certification", future(75), False),
                    ("Set up CI/CD pipeline for personal project", future(30), True),
                    ("Learn Terraform and infrastructure as code", future(60), False),
                    ("Contribute to a DevOps open source tool", future(90), False),
                ],
                "neethu_suresh": [
                    ("Complete thesis on social media anxiety", future(90), False),
                    ("Read 10 psychology books this semester", future(100), False),
                    ("Practice mindfulness for 30 days", future(25), False),
                ],
                "gautam_pandey": [
                    ("Validate business idea with 50 customer interviews", future(45), False),
                    ("Build landing page and collect leads", future(20), True),
                    ("Complete startup legal registration", future(30), False),
                    ("Find a co-founder", future(60), False),
                    ("Learn basics of digital marketing", past(15), True),
                ],
                "ishaan_chandra": [
                    ("Score 90%+ in board exams", future(60), False),
                    ("Learn guitar basics", future(90), False),
                    ("Complete 10th grade math syllabus revision", future(40), False),
                ],
                "roshni_alex": [
                    ("Get certified in advanced yoga training", future(120), False),
                    ("Grow Instagram to 5000 followers", future(90), False),
                    ("Build an online yoga course", future(150), False),
                ],
                "deepak_nair": [
                    ("Complete CA Inter Group 2", future(90), False),
                    ("Learn GST filing automation tools", future(60), False),
                    ("Exercise 3 times per week", past(30), False),
                ],
                "anjali_das": [
                    ("Submit research paper to journal", future(45), False),
                    ("Complete literature review for thesis", future(30), False),
                    ("Learn R for statistical analysis", future(60), False),
                    ("Present at one academic conference", future(120), False),
                ],
                "sundar_raj": [
                    ("Exceed Q2 sales target by 20%", future(45), False),
                    ("Build a CRM habit for daily follow-ups", future(30), False),
                    ("Complete negotiation skills course", past(10), True),
                ],
                "tejal_shah": [
                    ("Get certified in sports nutrition", future(90), False),
                    ("Create a 12-week meal plan product", future(60), False),
                    ("Grow client base to 20 active clients", future(120), False),
                ],
                "bharath_menon": [
                    ("Complete AutoCAD advanced certification", future(60), False),
                    ("Finish site report for Kovalam project", future(15), False),
                    ("Learn STAAD.Pro structural analysis", future(90), False),
                    ("Read 5 civil engineering case studies", past(20), True),
                ]
            }

            high_performers = ["arjun_menon", "sneha_pillai", "arun_thomas", "vikram_shetty", "siddharth_joshi", "nikhil_sharma", "vishnu_kumar"]
            lazy = ["priya_nair", "kavya_menon", "deepak_nair", "rahul_nambiar", "neethu_suresh", "ishaan_chandra", "sundar_raj"]
            moderate = ["rohan_das", "divya_krishna", "karthik_iyer", "meera_varma", "lakshmi_pillai", "anjali_das", "tejal_shah", "roshni_alex", "pooja_iyer", "ananya_reddy", "aditya_mehta", "shreya_bose", "gautam_pandey", "bharath_menon"]

            specific_tasks = {
                "Get AWS Solutions Architect Certified": [
                    ("Sign up for AWS free tier account", past(60), True),
                    ("Complete EC2 and S3 fundamentals module", past(45), True),
                    ("Finish VPC and networking section", past(30), True),
                    ("Complete IAM and security policies module", past(15), True),
                    ("Take 3 full practice exams", future(10), False),
                    ("Schedule and book exam slot", future(20), False),
                    ("Review weak areas and retake mock tests", future(30), False),
                ],
                "Run a 10K under 55 minutes": [
                    ("Start Couch to 5K training plan", past(40), True),
                    ("Run 3 times per week consistently", past(20), True),
                    ("Complete first 5K run", past(10), True),
                    ("Increase weekly mileage to 25 km", future(10), False),
                    ("Register for local 10K event", future(20), False),
                    ("Complete first timed 10K run", future(35), False),
                ],
                "Score 85%+ in semester exams": [
                    ("Create subject-wise study timetable", past(25), True),
                    ("Complete Data Structures notes", past(20), False),
                    ("Solve last 5 years question papers", past(10), False),
                    ("Attend all remaining lectures", future(10), False),
                    ("Form study group for exam prep", past(15), False),
                    ("Complete revision for all subjects", future(20), False),
                ],
                "Land 3 new freelance clients": [
                    ("Update Upwork profile and portfolio", past(30), True),
                    ("Send 20 cold emails to potential clients", past(20), True),
                    ("Apply to 10 LinkedIn job posts", past(10), False),
                    ("Follow up with 5 previous contacts", future(5), False),
                    ("Close first freelance contract", future(15), False),
                ],
                "Lose 8 kg in 3 months": [
                    ("Consult a nutritionist for diet plan", past(80), True),
                    ("Join a gym and start training", past(75), True),
                    ("Track calories daily using app", past(60), True),
                    ("Complete first month weight check-in", past(50), True),
                    ("Adjust diet based on progress", past(20), True),
                    ("Complete second month weigh-in", future(10), False),
                    ("Reach final target weight", future(90), False),
                ],
                "Launch MVP of SaaS product": [
                    ("Finalize product spec and wireframes", past(60), True),
                    ("Set up project GitHub repo and CI/CD", past(45), True),
                    ("Build user authentication module", past(30), True),
                    ("Complete core feature — dashboard", past(15), True),
                    ("Set up payment integration", future(10), False),
                    ("Run internal QA and bug fixes", future(25), False),
                    ("Deploy to production on AWS", future(40), False),
                    ("Announce launch on social media", future(45), False),
                ],
                "Complete thesis on social media anxiety": [
                    ("Finalize research question and scope", past(60), True),
                    ("Collect 50 survey responses", past(40), False),
                    ("Conduct 5 in-depth interviews", past(25), False),
                    ("Analyze data using SPSS", future(10), False),
                    ("Write literature review chapter", future(20), False),
                    ("Submit first draft to supervisor", future(45), False),
                ],
                "Complete CA Inter Group 2": [
                    ("Buy study material for Group 2", past(80), True),
                    ("Complete Financial Management chapter 1", past(60), False),
                    ("Solve past exam papers", past(30), False),
                    ("Enroll in revision batch", past(15), False),
                    ("Complete mock test series", future(20), False),
                ]
            }

            for username, goal_list in goals_data.items():
                user = users[username]
                for title, target_dt, is_completed in goal_list:
                    status = 'Completed' if is_completed else 'Active'
                    goal, _ = Goal.objects.get_or_create(
                        user=user, 
                        title=title, 
                        defaults={
                            'status': status,
                            'goal_type': 'task_based'
                        }
                    )

                    if title in specific_tasks:
                        for t_title, due, t_comp in specific_tasks[title]:
                            Task.objects.get_or_create(
                                user=user,
                                goal=goal,
                                title=t_title,
                                defaults={
                                    'due_date': due,
                                    'status': 'Completed' if t_comp else 'Pending'
                                }
                            )
                    else:
                        is_lazy = username in lazy
                        is_high = username in high_performers
                        t2_comp = True if is_high or username in moderate else False
                        t3_comp = True if is_high else False

                        Task.objects.get_or_create(user=user, goal=goal, title="Planning/setup task", defaults={'due_date': past(35), 'status': 'Completed'})
                        Task.objects.get_or_create(user=user, goal=goal, title="First execution step", defaults={'due_date': past(20), 'status': 'Completed' if t2_comp else 'Pending'})
                        Task.objects.get_or_create(user=user, goal=goal, title="Mid-goal milestone", defaults={'due_date': past(10), 'status': 'Completed' if t3_comp else 'Pending'})
                        Task.objects.get_or_create(user=user, goal=goal, title="Current active task", defaults={'due_date': future(5), 'status': 'Pending'})
                        Task.objects.get_or_create(user=user, goal=goal, title="Near-future checkpoint", defaults={'due_date': future(20), 'status': 'Pending'})
                        Task.objects.get_or_create(user=user, goal=goal, title="Final goal completion task", defaults={'due_date': target_dt, 'status': 'Pending'})

                # Standalone Tasks
                is_lazy = username in lazy
                Task.objects.get_or_create(user=user, goal=None, title="Reply to pending emails", defaults={'due_date': past(2), 'status': 'Pending' if is_lazy else 'Completed'})
                Task.objects.get_or_create(user=user, goal=None, title="Organize downloads folder", defaults={'due_date': past(5), 'status': 'Pending'})
                Task.objects.get_or_create(user=user, goal=None, title="Book dentist appointment", defaults={'due_date': future(7), 'status': 'Pending'})

            # STEP 4 — CREATE HABITS
            habits_data = {
                "arjun_menon": ["Morning Run", "Read Tech Blogs", "LeetCode Practice", "Drink 2L Water"],
                "priya_nair": ["Study 2 Hours", "Read Textbooks", "Avoid Social Media", "—"],
                "rohan_das": ["Code 1 Hour Daily", "Journaling", "Evening Walk", "—"],
                "sneha_pillai": ["Gym Workout", "Track Calories", "Yoga", "Sleep by 10:30 PM"],
                "karthik_iyer": ["CAT Practice Test", "Read Business News", "Meditate", "—"],
                "divya_krishna": ["Design 1 UI Screen", "Read Design Books", "Workout", "—"],
                "arun_thomas": ["Practice SQL Queries", "Read Analytics", "Morning Walk", "—"],
                "meera_varma": ["Read 30 Minutes", "Meditate", "Write in Journal", "—"],
                "vikram_shetty": ["Review KPIs", "Networking Call", "Exercise", "Read Startup News"],
                "ananya_reddy": ["Flashcard Revision", "Sleep 7 Hours", "Walk 30 Minutes", "—"],
                "siddharth_joshi": ["Code 2 Hours", "Read Tech Docs", "Gym", "—"],
                "kavya_menon": ["Write 500 Words", "Read 20 Pages", "—", "—"],
                "nikhil_sharma": ["Review Roadmap", "Read PM Content", "Exercise", "—"],
                "pooja_iyer": ["Journal", "Read HR Blogs", "Meditate", "—"],
                "rahul_nambiar": ["Study 3 Hours", "Coding Practice", "—", "—"],
                "shreya_bose": ["Design 1 Asset", "Sketch Practice", "Evening Run", "—"],
                "aditya_mehta": ["Read Finance News", "Excel Practice", "Walk", "—"],
                "lakshmi_pillai": ["Morning Walk", "Study Notes", "Meditate", "—"],
                "vishnu_kumar": ["Learn DevOps Daily", "Morning Run", "Read Tech Docs", "—"],
                "neethu_suresh": ["Mindful Breathing", "Read Psychology", "Journaling", "—"],
                "gautam_pandey": ["Cold Outreach", "Read Business", "Exercise", "—"],
                "ishaan_chandra": ["Study 2 Hours", "Practice Guitar", "—", "—"],
                "roshni_alex": ["Morning Yoga", "Post on Instagram", "Meditation", "—"],
                "deepak_nair": ["Study 1 Hour", "Morning Walk", "—", "—"],
                "anjali_das": ["Read Research Papers", "Write 300 Words", "Walk", "—"],
                "sundar_raj": ["Update CRM", "Read Sales Tips", "Exercise", "—"],
                "tejal_shah": ["Post Nutrition Tip", "Client Check-in", "Morning Yoga", "—"],
                "bharath_menon": ["Read Civil Eng News", "CAD Practice", "Evening Walk", "—"],
            }

            type_a = ["arjun_menon", "sneha_pillai", "arun_thomas", "vikram_shetty", "siddharth_joshi", "vishnu_kumar"]
            type_b = ["divya_krishna", "nikhil_sharma", "meera_varma", "anjali_das", "tejal_shah", "roshni_alex", "lakshmi_pillai", "gautam_pandey"]
            type_c = ["priya_nair", "rohan_das", "karthik_iyer", "pooja_iyer", "ananya_reddy", "neethu_suresh", "aditya_mehta", "sundar_raj", "ishaan_chandra", "shreya_bose", "bharath_menon"]
            type_d = ["deepak_nair"]

            for username, h_list in habits_data.items():
                user = users[username]
                for h_idx, h_name in enumerate(h_list):
                    if h_name != "—" and h_name:
                        habit, _ = Habit.objects.get_or_create(
                            user=user,
                            habit_name=h_name,
                            defaults={'habit_type': 'checkbox'}
                        )

                        # STEP 5 — CREATE HABIT COMPLETIONS
                        is_d = username in type_d or (username == "kavya_menon" and h_idx == 1) or (username == "rahul_nambiar" and h_idx == 1)
                        is_c = (username in type_c or username in ["kavya_menon", "rahul_nambiar"]) and not is_d

                        count = 0
                        for i in range(30, -1, -1):
                            day = past(i)
                            completed = False
                            
                            if username in type_a:
                                completed = True
                            elif username in type_b:
                                # Miss approx 1 per week (e.g., skip day 5, 12, 19, 26 offset somewhat)
                                # we'll use day modulus logic to achieve exactly this without weekday constraints if needed.
                                if i not in [5, 12, 19, 26]:
                                    completed = True
                            elif is_c:
                                # Incomplete last 3-5 days
                                if i <= 4:
                                    completed = False
                                else:
                                    pattern = (30 - i) % 7 # 0 to 6
                                    # Complete Mon-Wed (3 days), miss 2, complete 1, miss 1
                                    if pattern in [0, 1, 2, 5]:
                                        completed = True
                            elif is_d:
                                # inactive last 7 days
                                if i > 7:
                                    pattern = (30 - i) % 10
                                    if pattern < 3:
                                        completed = True

                            if completed:
                                HabitCompletion.objects.get_or_create(
                                    habit=habit,
                                    date=day,
                                    defaults={'completion_percentage': 100}
                                )

            # STEP 6 — VALIDATION CHECKS
            self.stdout.write(f"Users created:             {User.objects.count()}")
            self.stdout.write(f"Goals created:             {Goal.objects.count()}")
            self.stdout.write(f"Tasks created:             {Task.objects.count()}")
            self.stdout.write(f"  - Completed tasks:       {Task.objects.filter(status='Completed').count()}")
            self.stdout.write(f"  - Pending tasks:         {Task.objects.filter(status='Pending').count()}")
            self.stdout.write(f"Habits created:            {Habit.objects.count()}")
            self.stdout.write(f"Habit completions created: {HabitCompletion.objects.count()}")
            self.stdout.write("Seed complete. OK")
