# pip install pytest-playwright
# playwright install

# pip install ipython nest_asyncio
import asyncio
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from rich import print
import requests
import re

def dork(url, headless):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=headless)
        page = browser.new_page()
        page.goto(url)

        html_content = page.content()
        if not headless: input('...')
        browser.close()

        return html_content

def Parse(subject, headless=True):
    url = f"https://www.google.com/search?hl=en&q={subject.replace(' ', '+')}"
    print('\ninfo: now parsing '+url)
    html = dork(url, headless)
    soup = BeautifulSoup(html, 'html.parser')
    """soup = soup.find('div', id="res", role="main").find('div', id='rso', attrs={
        'data-async-context': True
        })"""

    response = Scraper(soup)
    if response:
        #print("Found!")
        print(response)
        return (True, str(response))
    else: 
        print('   ^', response)
        return (False, "")

"""
Featured snippets
/Knowledge panel
Answer box
/Images
Instant answer
People Also asked
Videos
Calculator
Definition
Local Pack
Map
Zero-click searches
Deploy schema markup
"""

days = {
    'Mon': 'Monday',
    'Tue': 'Tuesday',
    'Wed': 'Wednesday',
    'Thu': 'Thursday',
    'Fri': 'Friday',
    'Sat': 'Saturday',
    'Sun': 'Sunday',
}

tests = [
    'How to pronounce spaghetti',         # plugins_knowledge | sounds_like
    'Best hotels in London',              # section_filter /or/ plugins_hotel_sugg
    'What is the time in japan',          # section_card    | section_vk_card
    'bitcoin in dollars',                 # section_card    | finance_convertor
    'What is the date of today',          # section_card    | section_vk_card
    'How much is ten to the power of two',# section_card    | section_calculator
    'How to delete a facebook account',   # block_component | listings
    'How much is five dollars in euro',   # block_component | currency
    'how much bitcoin for ten thousand dollars', # block_component | table
    'Anthonyms of encounter',             # block_component | table
    'Advantages of using eletric cars',   # block_component | ulListing
    'How old is taylor swift',            # block_component | header_kp
    'How long until april 24',            # block_component | header_kp
    'How does airtag work',               # block_component | description_wa
    'Who created the create mod for mc',  # block_component | description_wa
    'Hello meaning',                      # block_words     | overview_tab
    'Hello in a sentence',                # block_words     | examples_tab
    'Synonyms of hello',                  # block_words     | similar_oposite_tab
    'Weather in London for tomorrow',     # container_ob    | weather_wob
    'How to say hello in korean',         # container_expandable | translator
    'How to say hello in spanish',        # container_expandable | translator
    'Distance between lisbon and porto',  # container_direction
    'Tesla stocks',                       # container_finance
    'where were you where they were also',# container_artist
    'Local coffee stores',                # container_map
    'Who is Elon Musk',                   # complementary
]

def getObjText(soup, obj):
    obj_group = soup.find_all(obj)
    text = None
    for _obj in obj_group:
        if len(_obj.find_all()) == 1:
            text = _obj.get_text(strip=True)
            return text
    return text

def checkWordsBlock(soup, osrp):
    block_words = soup.find('div', class_=osrp)
    if not block_words: return None
    block_words = block_words.find('div', role="tablist")
    if not block_words: return None
    block_tabs = block_words.find_all('span', attrs={
        'aria-selected': True,
        'data-ti': True,
        'tabindex': -1,
    }, role="tab")
    print('found -> type:<block> header')
    return soup
    
def Scraper(soup, debug=False):
    ## NOTES: 
    # here i'm discarting any dictionary knolage zci because the model should be able to respond to that alone.

    block_component = soup.find('block-component')
    block_words = checkWordsBlock(soup, 'kp-wholepage-osrp')
    complementary = soup.find('div', id='rhs', role='complementary')

    # we search for the block component before cus there might be info above the main res
    _soup = soup
    soup = soup.find('div', id="res", role="main").find('div', id='rso', attrs={
        'data-async-context': True
        }) if not block_component else soup
    container_ob = soup.find('div', class_=lambda x: x and 'obcontainer' in x)
    container_map = soup.find('div', style=lambda x: x and x.startswith("z-index:"))
    container_direction = soup.find('div', id="lud-ed", attrs={
        'data-async-type': "editableDirectionsSearch",
        'data-async-context-required': "directions_state",
    })
    container_finance = soup.find('div', attrs={
        'data-attrid': lambda x: x and x.startswith('kc:/finance'),
        'data-md': True
        })
    container_artist = _soup.find('span', attrs={
        'data-ti': lambda x: x and x.startswith('default_tab:action:listen_'),
        #'aria-selected': True,
        #'role': "tab"
    })
    container_expandable = soup.find('g-expandable-container')
    section_card = soup.find('div', class_=lambda x: x and 'card-section' in x)
    section_filter = soup.find('div', attrs={'aria-label': "Filters"}, role="form")
    section_artist = _soup.find('div', attrs={'data-maindata': lambda x: x and '["MUSIC"]' in x})
    plugins_knowledge = soup.find('div', class_=lambda x: x and "plugins-knowledge" in x)
    plugins_hotel_sugg = soup.find('div', attrs={'aria-label': "Hotel suggestions"})


    # <--- sections --->
    if section_card:
        #print(section_card)
        card_class = ' '.join(section_card.get('class'))
        section_vk_card = section_card if card_class.startswith('vk_gy vk_sh') else None
        finance_convertor = section_card.parent.find('div', attrs={
                'class': lambda x: x and 'card-section' in x,
                'data-attrid': "Converter"
            })
        try: section_calculator = next(Table for Table in section_card.find_all('tbody') if Table.find('tr'))
        except StopIteration: section_calculator = None
        if section_vk_card:
            print(section_vk_card) if debug else None
            head = section_vk_card.find('div', class_=lambda x: x and 'vk_bk' in x)
            place          = section_vk_card.find('span', class_="vk_gy vk_sh")
            section_vk_card = section_vk_card.find('div', class_="vk_gy vk_sh")
            if head and section_vk_card and place: return f"{place.text}: {head.text} | {section_vk_card.text}"
            if head and place:  return f"{place.text}: {head.text}"
            if section_vk_card: return section_vk_card.text
            if head:            return head.text
        if finance_convertor:
            status = finance_convertor.find('span', attrs={'class': True, 'aria-live': True, 'jsdata': True})
            exchange = finance_convertor.find('div', attrs={'data-exchange-rate': True, 'data-name': True})
            amount = exchange.parent.find('div', attrs={'data-exchange-rate': False, 'data-name': True}) if exchange else None
            if exchange and amount and status:
                if debug: print(exchange, amount)
                amount   = f"{amount.find('input').attrs.get('value')} {amount.attrs.get('data-name')}"
                exchange = f"{exchange.find('input').attrs.get('value')} {exchange.attrs.get('data-name')}"
                status = f"{status.find('span', attrs={'jsname': True}).text} {status.find('span', attrs={'aria-label': lambda x: x and 'by' in x and '%' in x}).attrs.get('aria-label')}"
                return f"{exchange} = {amount} | ({status})"

        if section_calculator: 
            # found the calc tables to make sure it's a calc obj
            section_calculator = [span for span in section_card.find_all('span', attrs={
                'aria-label': False, 'jsaction': False}) if span.text != ""]
            print(section_calculator) if debug else None
            if len(section_calculator) == 2:
                return f"Calculator: {section_calculator[0].text.replace('  ', '')} {section_calculator[1].text}"
    if section_filter:
        # very nasty code but should do the trick
        section_header = section_filter.parent
        section_places = section_header.parent
        guests = section_filter.find('div', role="button", attrs={
            'aria-label': lambda x: x and x.startswith('Select number of guests.'),
            'aria-haspopup': True,
            'tabindex': 0,
            })
        head = section_header.find('div', role="heading", attrs={'aria-level': True,})
        print(head, guests) if debug else None
        if head and guests and section_places:
            elements = []
            elements.append(f"{head.text} (for {guests.text} guests):")
            section_places = section_places.find_all('div', attrs={
                'jsaction': lambda x: x and x.startswith('mouseover:') and ';mouseout:' in x,
                'data-index': True,
                'data-key': True,
            })
            for place in section_places:
                place_name = place.find('div', id=lambda x: x and x.startswith('name_tsuid_'))
                place_rate = place.find('div', id=lambda x: x and x.startswith('rating_tsuid_'))
                place_price= place.find('div', id=lambda x: x and x.startswith('price_tsuid_'))
                place_price= 'Unknown pricings' if not place_price else place_price.get('aria-label')
                place_rate = 'Unknown ratings' if not place_rate else place_rate.find('span', role="img").get('aria-label')
                elements.append(f"{place_name.text}: {place_rate} | {place_price}")
            elements.append('Consult google maps for more details & directions.')
            return '\n · '.join(elements)
    if section_artist:
        section_artist = section_artist.parent
        if section_artist.find('a', attrs={
            'data-ti': "overview",
            'role': "link",
            }):
            title = section_artist.find('div', attrs={'data-attrid': "title", 'role': "heading"})
            subtitle = section_artist.find('div', attrs={'data-attrid': "subtitle", 'role': "heading"})
            if title and subtitle:
                subtitle, artist = subtitle.text.split('by') if 'by' in subtitle.text else [subtitle.text, ""]
                title = title.text + ' by'+artist if artist != "" else title.text

                return f'<action:Player> Music found: {title}'

    # <--- blocks --->
    if block_component:
        block_component = block_component.find('div', class_=lambda x: x and 'xpdopen' in x)
        currency = block_component.find('div', id="knowledge-currency__updatable-data-column")
        ulListing = block_component.find(lambda tag: tag.name == 'ul' and tag.find('li') is not None)
        description_wa = block_component.find('div', role="heading", attrs={
            'data-attrid': "wa:/description", 'aria-level': True,})
        header_kp = block_component.find('div', class_="kp-header")
        table = block_component.find('div', class_="webanswers-webanswers_table__webanswers-table")
        try: listings = next(ol for ol in block_component.find_all('ol') if ol.find('li'))
        except StopIteration: listings = None
        if currency:
            exchange_rate = currency.find('div', attrs={'data-exchange-rate': True})
            print(exchange_rate) if debug else None
            return exchange_rate.text.replace('equals', 'equals ')
        if listings: 
            elements = []
            head = next(div for div in block_component.find_all('div', role="heading") if div.find('b'))
            elements.append(head.text)
            for elm in listings:
                print(elm) if debug else None
                elements.append(str(listings.index(elm)+1) +' '+ elm.text)
            return '\n · '.join(elements)
        if header_kp:
            if header_kp.find('div', class_="kp-hc"):
                result = header_kp.text.replace('\xa0', ' ')
                return re.sub(r'([a-z])([A-Z])', r'\1 | \2', result)
        if ulListing:
            print(ulListing) if debug else None
            ulListing = ulListing.find_all('li')
            elements = []
            for tab in ulListing:
                elements.append(tab.text)
            return ' · '+'\n · '.join(elements)
            
        if table:
            title = table.parent.find('div', role="heading")
            table = table.find('tbody')
            if title and table and table.find('tr'):
                data = {'row1': [], 'row2': []}
                title = None
                table = table.find_all('tr')
                for row in table:
                    isTitle = row.find('th')
                    isTdRow = row.find('td')
                    if isTitle:
                        left_row = row.find('th', attrs={'style': True})
                        right_row = row.find('th', attrs={'style': False})
                        title = [left_row.text, right_row.text]
                        """data[left_row.text] = data.pop('row1')
                        data[right_row.text] = data.pop('row2S')"""
                    elif isTdRow:
                        left_row = row.find('td', attrs={'style': True})
                        right_row = row.find('td', attrs={'style': False})
                        if left_row and right_row:
                            data['row1'].append(left_row.text)
                            data['row2'].append(right_row.text)
                    else: pass
                if title != None or (title[0] and title[1]):
                    data[title[0]] = data.pop('row1')
                    data[title[1]] = data.pop('row2')

                if debug: print(data)

                converted_data = []
                for left_row, right_row in zip(data[title[0]], data[title[1]]):
                    #left_value, left_match = left_row.split(' ')
                    #right_value, right_match = right_row.split(' ')
                    converted_data.append(f"{left_row} - {right_row}")
                
                if converted_data != []:
                    return ' · '+'\n · '.join(converted_data)

                
        if description_wa: 
            # remove all bubble links
            g_bubbles = description_wa.find_all('g-bubble')
            description_wa = description_wa.text
            if g_bubbles: 
                g_bubbles_dict = {}
                for element in g_bubbles:
                    element_text = element.text
                    span_element = element.find('span', attrs={'data-segment-text': True}).text
                    g_bubbles_dict[element_text] = span_element
                print(g_bubbles_dict) if debug else None
                for key, value in g_bubbles_dict.items():
                    description_wa = description_wa.replace(key, value)
            return description_wa
    if block_words:
        # i'm gonna cry ;<
        # discard pronounciations, already in plugins
        overview_tab = soup.find('div', id="kp-wp-tab-overview")
        examples_tab = soup.find('div', id="kp-wp-tab-cont-g:UsageExamples", role="tabpanel")
        similar_oposite_tab = soup.find('div', id="kp-wp-tab-g:Thesaurus")
        block_component = soup.find('block-component')
        corpus = block_words.find('div', attrs={
            'data-query-term': True,
            'data-language': True,
            'data-robtew': True,
            'data-corpus': True,
            'data-hhdr': True,
            'data-dsk': True,
        })
        if overview_tab and corpus:
            overview_tab = overview_tab.find('div', id=lambda x: x and x.startswith('tsuid_'), class_="xpdbox xpdclose")
            overview_tab = overview_tab.find('div', class_=lambda x: x and 'lr_container' in x)
            if overview_tab.find('div', attrs={'data-attrid': "DictionaryHeader"}):
                overview_tab = overview_tab.find('div', attrs={
                    'data-attrid': "EntryHeader", 'data-psd': True
                    }).parent
                overview_tab = overview_tab.find_all('div', class_="vmod", attrs={'data-topic': True})
                elements = []
                for tab in overview_tab:
                    tab_name = tab.find('i').text
                    definition = tab.find('div', attrs={'data-attrid': "SenseDefinition"})
                    elements.append(f"{tab_name}: {definition.text}")
                return ' · '+'\n · '.join(elements)
        if examples_tab:
            examples_tab = examples_tab.find('div', id=lambda x: x and x.startswith('tsuid_'), class_="xpdbox xpdclose")
            if examples_tab:
                examples_tab = examples_tab.find('div', class_=lambda x: x and 'lr_container' in x)
                if examples_tab.find('div', attrs={'data-attrid': "UsageExample"}):
                    examples_tab = examples_tab.find_all('div', attrs={'data-attrid': "UsageExample", 'data-psd': True})
                    elements = []
                    elements.append('Usage examples:')
                    for tab in examples_tab:
                        elements.append(tab.text)
                    return '\n · '.join(elements)
        if similar_oposite_tab and block_component:
            similar_oposite_tab = similar_oposite_tab.find('div', class_=lambda x: x and 'xpdopen' in x)
            if similar_oposite_tab:
                try: ul_list = next(ul for ul in similar_oposite_tab.find_all('ul') if ul.find('li'))
                except StopIteration: ul_list = None
                webpages = similar_oposite_tab.find('div', class_="webanswers-webanswers_table__webanswers-table")
                try: web_list = next(Table for Table in webpages.find_all('tbody') if Table.find('tr'))
                except: web_list = None
                if ul_list:
                    elements = []
                    for tab in ul_list:
                        elements.append(tab.text)
                    return ' · '+'\n · '.join(elements)
                if webpages and web_list:
                    # VERY UNSTABLE; PLEASE CHECK
                    elements = []
                    webpages = webpages.parent
                    elements.append(webpages.find('div', role="heading", attrs={'aria-level': True}).text)
                    for table in web_list:
                        for td in table.find_all('td'):
                            elements.append(td.text)
                    return '\n · '.join(elements)
    
    # <--- containers --->
    if container_ob:
        weather_wob = container_ob.find('div', id='wob_wc')
        if weather_wob:
            rain = weather_wob.find('span', id="wob_pp").text
            humidity = weather_wob.find('span', id="wob_hm").text
            winds = weather_wob.find('span', id="wob_ws", class_="wob_t").text
            current_temp = weather_wob.find('span', id="wob_tm").text
            temp_scale = weather_wob.find('span', class_="wob_t",  style="display:inline", role="button").text
            day_pannel = weather_wob.find('div', id="wob_dp", class_="wob_dfc")
            day_pannel = day_pannel.find('div', class_="wob_df wob_ds", role="button")
            day_name = days[day_pannel.find('div').text]
            day_pannel = day_pannel.find_all('span', class_="wob_t", style="display:inline")
            return f"Forecast for {day_name}:\n · " + '\n · '.join([
                'Rain: '+rain,
                'Humidity: '+humidity,
                'Winds: '+winds,
                'Temp: '+current_temp+' '+temp_scale,
                'High: '+day_pannel[0].text,
                'Low: '+day_pannel[1].text,
                'Consult the Google weather forecast for more details.',
            ])
    if container_map:
        places = []
        container_map = container_map.find_all(
        'div', id=lambda x: x and x.startswith('tsuid'), attrs={
        'data-record-click-time': True,
        'jscontroller': True,
        'data-hveid': True,
        'jsaction': True,
        'jsdata': True,
        })
        if container_map:
            for place in container_map:
                rating = place.find('span', role="img", attrs={'aria-label': True})
                # find a div that only contains a string inside it (for location)
                street = place.find(lambda tag: tag.name == 'div' and tag.string is not None and not tag.find())
                place = place.find('div', role="heading", attrs={'aria-level': True})
                print(place, rating, street) if debug else None
                if place: 
                    rating = 'Unknown ratings' if rating == None else rating.get('aria-label')
                    street = 'Unknown location' if street ==None else street.text
                    places.append(" | ".join([place.text.replace(', ', ' '), rating, street]))
            places.append('Consult the Google for more details.')
            return ' · '+'\n · '.join(places)
    if container_direction:
        place_from = container_direction.find('input', attrs={'aria-label': "From", 'placeholder': True})
        place_to   = container_direction.find('input', attrs={'aria-label': "To", 'placeholder': True})
        container_map = container_direction.find('div', id="map_container")
        container_direction = container_direction.find('div', id="lud-search", attrs={
            'data-async-context-required': "directions_state",
            'data-async-type': "routeSearch",
        })
        if place_from and place_to:
            place_from = place_from.get('placeholder')
            place_to = place_to.get('placeholder')
        if not place_from and not place_to and container_map:
            # new ui update???
            print('fail: fetch place -> using map module')
            place_from = container_map.attrs.get('title').split(' to ')[0].replace('Map from ', '')
            place_to = container_map.attrs.get('title').split(' to ')[1]
        if container_direction and place_from and place_to:
            elements = []
            print(place_from, place_to) if debug else None
            elements.append(f"From {place_from} to {place_to}: ")
            directions = container_direction.find_all('div', id=lambda x: x and x.startswith('exp'),
                                                      attrs={'data-rre-route-idx': True},
                                                      role="listitem")
            for direction in directions:
                direction_ids = direction
                direction = direction.find('div', attrs={'aria-hidden': False})
                direction = direction.text.replace('Directions', '', -1)
                elements.append(direction + ' (best)' if direction_ids.get('data-rre-route-idx') == '0' else direction)
            elements.append('Consult Google Maps for more information & directions.')
            return '\n · '.join(elements)      
    if container_finance:
        name = container_finance.find('span', attrs={'data-attrid': "Company Name"}).text
        container_finance = container_finance.find('g-card-section').find('div', attrs={
            'data-attrid': "Price"
            })
        stats = container_finance.find('span', class_=lambda x: x and 'fw-price-' in x)
        diff  = stats.find('span', attrs={'aria-label': True}).get('aria-label')  
        stats = stats.find('span', attrs={'jsname': True}).text
        price = container_finance.find('span').text
        return f"{name} | {price} ({stats} {diff})"
    if container_artist:
        # found listen button
        print(1)
        container_artist = _soup.find('div', class_=lambda x: x and 'kp-wholepage-osrp' in x)
        title = container_artist.find('div', attrs={
            'data-attrid': "title",
            'role': "heading",
        })
        subtitle = container_artist.find('div', attrs={
            'data-attrid': "subtitle",
            'role': "heading",
        })
        if title and subtitle:
            subtitle, artist = subtitle.text.split('by') if 'by' in subtitle.text else [subtitle.text, ""]
            title = title.text + ' by'+artist if artist != "" else title.text

            return f'<action:Player> Music found: {title}'
    if container_expandable:
        translator = container_expandable.find('div', attrs={'data-entityname': "Google Translate",})

        if translator:
            indent_translator = container_expandable.find('div', attrs={
                'id': "tw-plp",
                'data-attrid': "tw-targetArea",
                'data-entityname': "Google Translate",})
            translator = container_expandable.find('div', id="tw-ob")
            source_translator = translator.find('div', attrs={
                'data-attrid': "tw-sourceArea",
                'data-entityname': "Google Translate",})
            target_translator = translator.find('div', attrs={
                'id': "tw-target",})
            if indent_translator and source_translator and target_translator:
                indent_translator = {
                    'source': indent_translator.find('div', id="tw-sl").text.replace(' - detected', ''),
                    'target': indent_translator.find('div', id="tw-tl").text,
                }
                source_translator = f"Original {indent_translator['source']} text: {source_translator.find('div', id='tw-source-text-container').find('span').text}"
                target_phonetic = target_translator.find('div', id="tw-target-rmn-container")
                if not target_phonetic or target_phonetic.text == '...':
                    target_translator = f"Direct {indent_translator['target']} translation: '{target_translator.find('div', id='tw-target-text-container').text.replace('...', '', -1)}'."
                else: target_translator = f"Phonetic {indent_translator['target']} translation: '{target_phonetic.text.replace('...', '', -1)}'."
                print(f"{source_translator}\n{target_translator}\n{indent_translator}") if debug else None
                return f"· {source_translator} \n· {target_translator}"

    # <--- plugins --->
    if plugins_knowledge:
        vert_lang_pronunciation = plugins_knowledge.find('div', attrs={
            'data-pronunciation-country': True,
            'data-pronunciation-language': True,
            'data-pronunciation-speed': True,
            'data-pronunciation-term': True
        })
        term = vert_lang_pronunciation.get('data-pronunciation-term')
        lang = plugins_knowledge.find('div', attrs={'aria-label': "Accent selector"})
        lang= lang.text if lang else None
        #lang = vert_lang_pronunciation.get('data-pronunciation-language')
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        sounds_like = plugins_knowledge.find('div', attrs={'data-attrid': "SoundsLike", 'aria-label': True})
        if vert_lang_pronunciation and sounds_like and lang:
            elements = []
            sounds_like = sounds_like.find_all('span', attrs={'data-syllable-duration': True})
            for sound in sounds_like: 
                if sound.text != "": elements.append(sound.text)
            return f"'{term}' in {lang} sounds like: {'-'.join(elements)}"
    if plugins_hotel_sugg:
        carousel = soup.find_all('image-carousel')
        if carousel != []:
            elements = []
            for place in carousel:
                place = place.parent.find('div', id=lambda x: x and x.endswith('_lbl'))
                place = place.select(f"div.{place.get('class')[0]} > *")
                if len(place) > 1 and len(place) < 4:
                    place_name = getObjText(place[0], 'div')
                    place_price= place[0].find('span').text
                    place_rate = place[1].find('span', attrs={'role': "img", 'aria-label': True}).get('aria-label')
                    if debug:
                        print(place[0], place[1])
                        print(place_name, place_price, place_rate)
                        print('*'*60)
                    elements.append(f"{place_name}: {place_rate} | prices starting from {place_price}")
            elements.append('Consult google maps for more details & directions.')
            return ' · '+'\n · '.join(elements)


    
    if complementary:
        # complementary object should always be the last one to be checked
        about = complementary.find('div', attrs={'aria-level': True, 'role': 'heading'})
        if about and about.text:
            desc = complementary.find('div', attrs={'data-attrid': "description"})
            print(desc) if debug else None
            elements = complementary.find_all('div', attrs={
                'data-attrid': lambda y: y and y.startswith('kc:/')
            })
            if elements != []:
                elements = [element.text for element in elements]
                elements = '\n · '+'\n · '.join(elements)
            else: elements = ""
            desc = getObjText(desc, 'span')
            return f"{about.text}: {desc}"+elements

        


        
    print('<[italic red] Result not found! [/italic red]>')
    return False

if __name__ == "__main__":
    q = input('*')
    if q == "":
        for i in tests:
            Parse(i)
    else: print('"""', Parse(q, headless=False), '"""')