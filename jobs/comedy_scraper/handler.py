from datetime import datetime, UTC
from shared.aws import default_handler
from shared.scraper import get_soup
from shared.aws import send_sns_notification, get_db_items, set_db_items

def scrape_comedy_shows():
    soup = get_soup("https://comedymothership.com/shows")
    
    shows = []
    all_show_cards = soup.find_all('div', class_='EventCard_textWrapper__P_Avg')
    
    for card in all_show_cards:
        # Title wrapper is first child
        title_wrapper = card.find_all('div')[0]
        # Get date and title
        date = title_wrapper.find('div').text.strip()
        title = title_wrapper.find('h3').text.strip()
        # Details list
        details_list = card.find('ul')
        time = details_list.find('li').text.strip()
        # Combine date and time
        date_time = f"{date} {time}"
        # Check if "Sold Out" text exists anywhere in the card
        sold_out = 'Sold Out' in card.get_text()
        
        show = {
            'id': f"{title}-{date_time.replace(' ', '').replace(':', '')}".replace(' ', '-').replace(',', ''),
            'title': title,
            'date_time': date_time,
            'sold_out': sold_out,
            'scraped_at': datetime.now(UTC).isoformat()
        }
        shows.append(show)
    return shows


DB_TABLE = 'comedy-mothership-shows'

def store_shows(shows):
    new_shows = []
    new_sold_out_shows = []
    newly_sold_out_shows = []
    newly_unsold_out_shows = []
    matching_existing_shows = get_db_items([show['id'] for show in shows], DB_TABLE)
    matching_existing_show_ids = [show['id'] for show in matching_existing_shows]
    for show in shows:
        try:
            # Try to get existing show
            if show['id'] not in matching_existing_show_ids:
                # Show doesn't exist, add it
                if show['sold_out']:
                    new_sold_out_shows.append(show)
                else:
                    new_shows.append(show)
            elif show['sold_out'] != matching_existing_shows[matching_existing_show_ids.index(show['id'])]['sold_out']:
                # Show exists but sold out status is different, update it
                if not show['sold_out']:
                    newly_unsold_out_shows.append(show)
                else:
                    newly_sold_out_shows.append(show)
        except Exception as e:
            print(f"Error storing show: {e}")
            continue
    
    new_or_updated_shows = new_shows + new_sold_out_shows + newly_sold_out_shows + newly_unsold_out_shows
    set_db_items(new_or_updated_shows, DB_TABLE)

    return new_shows, new_sold_out_shows, newly_unsold_out_shows


def comedy_scraper(added_logging=False):
    # Scrape shows
    shows = scrape_comedy_shows()
    message = ""
    # Store shows and get new ones
    new_shows, new_sold_out_shows, unsold_out_shows = store_shows(shows)

    
    # Send notification if there are new shows
    if new_shows:
        message = f"Found {len(new_shows)} new shows:\n"
        for show in new_shows:
            message += f"{show['title']} on {show['date_time']}\n"
    if new_sold_out_shows:
        message += f"Some shows sold out before you even saw them:\n"
        for show in new_sold_out_shows:
            message += f"{show['title']} on {show['date_time']}\n"
    if unsold_out_shows:
        message += f"Some shows are no longer sold out:\n"
        for show in unsold_out_shows:
            message += f"{show['title']} on {show['date_time']}\n"

    if message != "":
        if added_logging:
            print(message)
        send_sns_notification(message)

if __name__ == '__main__':
    print('Running comedy scraper...')
    comedy_scraper(True)

def lambda_handler(event, context):
    return default_handler(comedy_scraper, 'Successfully processed shows.')
