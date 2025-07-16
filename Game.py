import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Border Seeker: Acaristan")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (100, 100, 100)
GOLD = (212, 175, 55)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)

# Fonts
font = pygame.font.SysFont('Arial', 24)
title_font = pygame.font.SysFont('Arial', 36, bold=True)
lore_font = pygame.font.SysFont('Arial', 16)  # Smaller font for lore
fax_font = pygame.font.SysFont('Courier New', 18)  # Monospace font for fax

# Game state
game_state = "lore"  # lore, menu, game, game_over, ending
day = 1
reputation = 75
bribe_money = 0
anca_risk = 1  # Starting at 1% as requested
documents_processed = 0
special_event_triggered = False
news_messages = []

# Timing variables
last_click_time = 0
click_cooldown = 0.5  # 0.5 seconds cooldown
day_review_start_time = 0
day_review_duration = 2  # 2 seconds for day review

# Expanded documents list with new prank documents
documents = [
    # Legal documents
    {"title": "Military Parade Budget", "type": "legal", "bribe": 0, "risk": 0},
    {"title": "Border Wall Construction", "type": "legal", "bribe": 0, "risk": 0},
    {"title": "Public School Funding", "type": "legal", "bribe": 0, "risk": 0},
    
    # Questionable documents
    {"title": "Mayor's Nephew Permit", "type": "questionable", "bribe": 150, "risk": 3},
    {"title": "Medical Supply Order", "type": "questionable", "bribe": 200, "risk": 4},
    {"title": "Oil Export License", "type": "questionable", "bribe": 300, "risk": 5},
    {"title": "School Textbook Approval", "type": "questionable", "bribe": 100, "risk": 2},
    
    # Illegal documents
    {"title": "Subsidy for Fighting Pigs", "type": "illegal", "bribe": 250, "risk": 5},
    {"title": "Presidential Palace Renovation", "type": "illegal", "bribe": 350, "risk": 7},
    {"title": "Opposition Rally Ban", "type": "illegal", "bribe": 400, "risk": 8},
    
    # Highly illegal documents
    {"title": "Propaganda Funds", "type": "highly illegal", "bribe": 400, "risk": 8},
    {"title": "Opposition Leader Passport", "type": "highly illegal", "bribe": 500, "risk": 10},
    {"title": "Election Result Override", "type": "highly illegal", "bribe": 600, "risk": 12},
    
    # Prank documents
    {"title": "Andrei's Fake Passport", "type": "prank", "bribe": 0, "risk": 0},
    {"title": "MOSKOVACI Comeback Tour", "type": "prank", "bribe": 0, "risk": 0},
    {"title": "Free Vodka for All", "type": "prank", "bribe": 0, "risk": 0}
]

current_docs = []
current_doc_index = 0
day_ended = False
processing_document = False
show_fax = False

# Lore text
lore_text = [
    "Acaristan, 2025. The once-great nation has fallen into corruption and decay.",
    "As a border control officer, you process documents that cross your desk daily.",
    "The Anti-National Corruption Agency (ANCA) watches everyone closely.",
    "",
    "Legal documents are routine, but questionable ones offer... opportunities.",
    "Questionable: Reputation ±1",
    "Illegal: Reputation -10",
    "Highly Illegal: Reputation -35",
    "Prank documents have no effect",
    "",
    "Take bribes to enrich yourself, but risk ANCA investigation.",
    "Or stay honest and survive on your meager salary.",
    "",
    "The choice is yours. How will you survive 30 days in Acaristan?"
]

def draw_button(text, x, y, width, height, color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    current_time = time.time()
    
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, hover_color, (x, y, width, height))
        if click[0] == 1 and current_time - last_click_time > click_cooldown and not processing_document:
            return True
    else:
        pygame.draw.rect(screen, color, (x, y, width, height))
    
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=(x + width/2, y + height/2))
    screen.blit(text_surf, text_rect)
    return False

def start_new_day():
    global current_docs, current_doc_index, day_ended, documents_processed, processing_document
    # Random number of documents per day (1-4)
    num_docs = random.randint(1, 4)
    current_docs = random.sample(documents, num_docs)
    current_doc_index = 0
    day_ended = False
    documents_processed = 0
    processing_document = False

def draw_lore():
    screen.fill(BLACK)
    
    title = title_font.render("Border Seeker: Acaristan", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
    
    for i, line in enumerate(lore_text):
        if line:  # Skip empty lines
            text = lore_font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 120 + i * 25))
    
    if draw_button("Continue", SCREEN_WIDTH//2 - 100, 500, 200, 50, GREEN, (100, 255, 100)):
        global game_state
        game_state = "menu"

def draw_menu():
    screen.fill(GRAY)
    
    title = title_font.render("Border Seeker: Acaristan", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    
    subtitle = font.render("A Bureaucratic Corruption Simulator", True, WHITE)
    screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 160))
    
    if draw_button("Start Game", SCREEN_WIDTH//2 - 100, 250, 200, 50, GREEN, (100, 255, 100)):
        global game_state
        game_state = "game"
        start_new_day()
    
    if draw_button("Quit", SCREEN_WIDTH//2 - 100, 320, 200, 50, RED, (255, 100, 100)):
        pygame.quit()
        sys.exit()

def process_document_decision(decision):
    global current_doc_index, reputation, bribe_money, anca_risk, documents_processed, last_click_time, processing_document
    doc = current_docs[current_doc_index]
    last_click_time = time.time()  # Update last click time
    processing_document = True
    
    if decision == "approve":
        if doc["type"] == "questionable":
            reputation += random.choice([-1, 1])
        elif doc["type"] == "illegal":
            reputation -= 10
        elif doc["type"] == "highly illegal":
            reputation -= 35
        # No reputation change for legal or prank documents
    
    elif decision == "reject":
        if doc["type"] == "questionable":
            reputation += random.choice([-1, 1])
        elif doc["type"] in ["illegal", "highly illegal"]:
            reputation += 5  # Small boost for rejecting bad docs
    
    elif decision == "bribe":
        bribe_money += doc["bribe"]
        anca_risk = min(100, anca_risk + doc["risk"])
        reputation -= random.randint(3, 5)
    
    documents_processed += 1
    current_doc_index += 1
    
    # Add a small delay before allowing next action
    pygame.time.delay(300)
    processing_document = False

def draw_fax_machine():
    screen.fill(BLACK)
    
    # Draw fax machine outline
    pygame.draw.rect(screen, GRAY, (100, 80, 600, 440))
    pygame.draw.rect(screen, WHITE, (120, 100, 560, 400))
    
    # Draw fax header
    header = fax_font.render("=== ACARISTANI NEWS FAX ===", True, BLACK)
    screen.blit(header, (SCREEN_WIDTH//2 - header.get_width()//2, 120))
    
    # Draw news messages
    for i, message in enumerate(news_messages[-5:]):  # Show last 5 messages
        text = fax_font.render(message, True, BLACK)
        screen.blit(text, (140, 160 + i * 30))
    
    # Draw close button
    if draw_button("Close", SCREEN_WIDTH//2 - 50, 500, 100, 50, RED, (255, 100, 100)):
        global show_fax
        show_fax = False

def handle_special_event():
    global reputation, bribe_money, anca_risk, news_messages, special_event_triggered
    
    event_text = [
        "URGENT: Minister of Potatoes Scandal!",
        "",
        "Acaristan's Minister of Potatoes is under",
        "backlash after Bodi saw him steal 15 Liters",
        "of beer from him. He wants to leave the country.",
        "",
        "He offers you $2000 to let him pass, but",
        "this carries a massive 25% ANCA risk!"
    ]
    
    pygame.draw.rect(screen, WHITE, (150, 100, 500, 350))
    
    for i, line in enumerate(event_text):
        text = font.render(line, True, BLACK)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 120 + i * 30))
    
    if draw_button("Accept Bribe", 200, 400, 150, 50, GOLD, (212, 175, 55)):
        bribe_money += 2000
        anca_risk = min(100, anca_risk + 25)
        reputation -= 15
        news_messages.append("Minister of Potatoes killed by Rogue Acaristani Dogs in Kokoland")
        special_event_triggered = True
        return True
    
    if draw_button("Refuse", 450, 400, 150, 50, GREEN, (100, 255, 100)):
        reputation += 10
        news_messages.append("Minister of Potatoes now in prison after stealing")
        special_event_triggered = True
        return True
    
    return False

def draw_game():
    global day, game_state, day_ended, day_review_start_time, show_fax
    
    screen.fill(GRAY)
    
    # Draw stats
    stats = f"Day: {day}/30 | Rep: {reputation} | Bribes: ${bribe_money} | ANCA Risk: {anca_risk}%"
    stats_text = font.render(stats, True, WHITE)
    screen.blit(stats_text, (20, 20))
    
    # Draw fax button
    if len(news_messages) > 0:
        fax_button = draw_button("News Fax", 650, 20, 120, 30, YELLOW, (255, 255, 100))
        if fax_button:
            show_fax = True
    
    # Check for special event on day 15
    if day == 15 and not special_event_triggered:
        if handle_special_event():
            return
    
    if show_fax:
        draw_fax_machine()
        return
    
    if not day_ended and current_doc_index < len(current_docs):
        doc = current_docs[current_doc_index]
        
        # Draw document
        pygame.draw.rect(screen, WHITE, (100, 100, 600, 300))
        title = font.render(doc["title"], True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
        
        doc_type = font.render(f"Type: {doc['type']}", True, BLACK)
        screen.blit(doc_type, (SCREEN_WIDTH//2 - doc_type.get_width()//2, 200))
        
        if doc["bribe"] > 0:
            bribe_info = font.render(f"Bribe: ${doc['bribe']} (Risk: +{doc['risk']}%)", True, BLACK)
            screen.blit(bribe_info, (SCREEN_WIDTH//2 - bribe_info.get_width()//2, 250))
        
        # Special text for prank documents
        if doc["title"] == "Andrei's Fake Passport":
            prank_text = font.render("(This is clearly one of Andrei's pranks)", True, RED)
            screen.blit(prank_text, (SCREEN_WIDTH//2 - prank_text.get_width()//2, 280))
        elif doc["title"] == "MOSKOVACI Comeback Tour":
            prank_text = font.render("(MOSKOVACI will never return to music)", True, RED)
            screen.blit(prank_text, (SCREEN_WIDTH//2 - prank_text.get_width()//2, 280))
        
        # Draw buttons
        current_time = time.time()
        if current_time - last_click_time > click_cooldown and not processing_document:
            if draw_button("Approve", 150, 450, 150, 50, GREEN, (100, 255, 100)):
                process_document_decision("approve")
                
            if draw_button("Reject", 325, 450, 150, 50, RED, (255, 100, 100)):
                process_document_decision("reject")
                
            if doc["bribe"] > 0 and draw_button("Take Bribe", 500, 450, 150, 50, GOLD, (212, 175, 55)):
                process_document_decision("bribe")
        else:
            # Draw disabled buttons during cooldown
            pygame.draw.rect(screen, (200, 200, 200), (150, 450, 150, 50))
            pygame.draw.rect(screen, (200, 200, 200), (325, 450, 150, 50))
            if doc["bribe"] > 0:
                pygame.draw.rect(screen, (200, 200, 200), (500, 450, 150, 50))
            
            text_surf = font.render("Approve", True, (100, 100, 100))
            screen.blit(text_surf, (150 + 75 - text_surf.get_width()//2, 450 + 25 - text_surf.get_height()//2))
            
            text_surf = font.render("Reject", True, (100, 100, 100))
            screen.blit(text_surf, (325 + 75 - text_surf.get_width()//2, 450 + 25 - text_surf.get_height()//2))
            
            if doc["bribe"] > 0:
                text_surf = font.render("Take Bribe", True, (100, 100, 100))
                screen.blit(text_surf, (500 + 75 - text_surf.get_width()//2, 450 + 25 - text_surf.get_height()//2))
    
    elif not day_ended:
        day_ended = True
        day_review_start_time = time.time()
        # Show end of day summary
        summary = [
            f"Day {day} complete!",
            f"Documents processed: {documents_processed}",
            f"Current reputation: {reputation}",
            f"ANCA Risk: {anca_risk}%"
        ]
        
        pygame.draw.rect(screen, WHITE, (200, 150, 400, 300))
        for i, line in enumerate(summary):
            text = font.render(line, True, BLACK)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i * 50))
        
        # Only allow continuing after the review duration has passed
        if time.time() - day_review_start_time > day_review_duration:
            if draw_button("Continue", SCREEN_WIDTH//2 - 100, 450, 200, 50, BLUE, (100, 100, 255)):
                end_day()
    
    else:
        end_day()

def end_day():
    global day, anca_risk, game_state, reputation
    
    # Daily risk decay
    anca_risk = max(1, anca_risk - random.randint(1, 3))  # Never goes below 1%
    
    # Random events
    if random.random() < 0.3:  # 30% chance of inspection
        if random.random() < anca_risk/100:
            game_state = "game_over"
            return
    
    day += 1
    
    # Check for day 30 ending
    if day > 30:
        if bribe_money >= 10000:
            game_state = "corruption_ending"
        elif bribe_money > 0:
            game_state = "average_ending"
        else:
            game_state = "honest_ending"
    # Check game over conditions
    elif reputation <= 0 or anca_risk >= 100:
        game_state = "game_over"
    else:
        start_new_day()

def draw_game_over():
    screen.fill(GRAY)
    
    game_over_text = title_font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 100))
    
    if reputation <= 0:
        reason = font.render("Your reputation collapsed completely!", True, WHITE)
    else:
        reason = font.render("ANCA caught you taking bribes!", True, WHITE)
    
    screen.blit(reason, (SCREEN_WIDTH//2 - reason.get_width()//2, 160))
    
    stats = [
        f"Days survived: {min(day, 30)}",
        f"Total bribes: ${bribe_money}",
        f"Final reputation: {reputation}",
        f"Final ANCA risk: {anca_risk}%"
    ]
    
    for i, stat in enumerate(stats):
        stat_text = font.render(stat, True, WHITE)
        screen.blit(stat_text, (SCREEN_WIDTH//2 - stat_text.get_width()//2, 220 + i * 40))
    
    if draw_button("Main Menu", SCREEN_WIDTH//2 - 100, 400, 200, 50, BLUE, (100, 100, 255)):
        reset_game()

def draw_ending(ending_type):
    if ending_type == "corruption":
        screen.fill(PURPLE)
        title = title_font.render("CORRUPTION OVERLORD", True, GOLD)
        desc = font.render("You amassed great wealth through corruption!", True, WHITE)
        stats = f"Final bribe total: ${bribe_money}"
    elif ending_type == "average":
        screen.fill(BLUE)
        title = title_font.render("AVERAGE ACARISTANI", True, WHITE)
        desc = font.render("You took some bribes but didn't go overboard.", True, WHITE)
        stats = f"Final bribe total: ${bribe_money}"
    else:
        screen.fill(GREEN)
        title = title_font.render("HONEST OFFICIAL", True, WHITE)
        desc = font.render("You survived without taking dirty money!", True, WHITE)
        stats = "You took $0 in bribes"
    
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
    screen.blit(desc, (SCREEN_WIDTH//2 - desc.get_width()//2, 160))
    
    stats_text = font.render(stats, True, WHITE)
    screen.blit(stats_text, (SCREEN_WIDTH//2 - stats_text.get_width()//2, 220))
    
    # Show news highlights
    if len(news_messages) > 0:
        news_title = font.render("News Highlights:", True, WHITE)
        screen.blit(news_title, (SCREEN_WIDTH//2 - news_title.get_width()//2, 280))
        
        for i, message in enumerate(news_messages[-3:]):  # Show last 3 news items
            news_item = font.render(message, True, WHITE)
            screen.blit(news_item, (SCREEN_WIDTH//2 - news_item.get_width()//2, 320 + i * 30))
    
    if draw_button("Main Menu", SCREEN_WIDTH//2 - 100, 500, 200, 50, BLUE, (100, 100, 255)):
        reset_game()

def reset_game():
    global day, reputation, bribe_money, anca_risk, game_state, special_event_triggered, news_messages
    day = 1
    reputation = 75
    bribe_money = 0
    anca_risk = 1  # Reset to 1%
    game_state = "menu"
    special_event_triggered = False
    news_messages = []

# Main game loop
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    if game_state == "lore":
        draw_lore()
    elif game_state == "menu":
        draw_menu()
    elif game_state == "game":
        draw_game()
    elif game_state == "game_over":
        draw_game_over()
    elif game_state == "corruption_ending":
        draw_ending("corruption")
    elif game_state == "average_ending":
        draw_ending("average")
    elif game_state == "honest_ending":
        draw_ending("honest")
    
    pygame.display.flip()
    clock.tick(60)
