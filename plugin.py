import sublime
import sublime_plugin
import urllib.request
import re
import json


api_key = ''  # Set your API key here
api_url = 'https://wax-prd1-uae.wallyax.com/lint/html'


class WaxLinterCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        document_text = self.view.substr(sublime.Region(0, self.view.size()))
        file_name = self.view.file_name()
        
        if is_supported_file_type(file_name):
            html_code = extract_html_from_text(self.view, document_text)
            analyse_code = analyse(html_code, api_key)
            display_analysis_results(self, analyse_code)

        else:
            self.view.set_status('wax_linter_message', "Unsupported file type")


def is_supported_file_type(file_name):
    return file_name.endswith(('.html', '.js', '.jsx', '.ts', '.tsx', '.php', '.vue', '.astro', '.svelte'))


def extract_html_from_text(view, text):
    regex = re.compile(r'(<[^>]+>|[^<]+)')
    matches = {'htmlStrings': [], 'htmlObject': []}
    pos = 0

    for match in regex.finditer(text):

        matched_content = match.group(0).strip().replace('\s+', ' ')

        position = view.text_point(pos, match.start())
        line_number = view.rowcol(position)[0] + 1  # Add 1 because lines are zero-based in Sublime

        if matched_content.startswith('<') and not matched_content.startswith('</'):

            if matched_content.endswith('/>'):
                modified_content = matched_content.replace('/>', f' wax-ln="{line_number}" />')
            else:
                modified_content = matched_content.replace('>', f' wax-ln="{line_number}">')
            matches['htmlObject'].append({
                'lineNumber': line_number,
                'character': view.rowcol(position)[1],
                'element': modified_content
            })
        else:
            if matched_content == '':
                continue

            matches['htmlObject'].append({
                'lineNumber': line_number,
                'character': view.rowcol(position)[1],
                'element': matched_content
            })

    html_strings = [obj['element'] for obj in matches['htmlObject']]
    matches['htmlStrings'] = [extract_html_from_xml(''.join(html_strings))]

    return matches


def extract_html_from_xml(html_code):
    html_regex = re.compile(r'\s*\(\s*(<([a-zA-Z]+)[^>]*>.*?</\2>|<([a-zA-Z]+)\s+[^/>]+?/>)\s*\);', re.DOTALL)
    html_string = ''

    for match in html_regex.finditer(html_code):
        html = match.group(0)

        html = html.replace('{`', '').replace('`}', '')
        html = re.sub(r'\$\{[^\}]+\}', '', html)
        html_string += f'<{html.strip()}>\n'

    return html_string.strip() or html_code


def analyse(html_code, api_key):
    return analyse_wally(html_code, api_key)


def analyse_wally(html_code, api_key):
    try:
        data = json.dumps({'element': ''.join(html_code['htmlStrings']), 'isLinter': True}).encode()
        req = urllib.request.Request(f'{api_url}?apikey={api_key}', data=data, headers={'Content-Type': 'application/json'}, method='POST')
        response = urllib.request.urlopen(req)
        if response.status == 200:
            analysis_results = map_results_to_lines(json.loads(response.read().decode()))
            return analysis_results

    except Exception as error:
        self.view.set_status('wax_linter_message', f"We were not able to process your request: {error}")

    return []

def get_line_number(html_tag):
    match = re.search(r' wax-ln="(\d+)"', html_tag)

    if match:
        return int(match.group(1))

    return None

def map_results_to_lines(analysis_results):
    mapped_results = []

    for result in analysis_results:
        result['lineNumber'] = get_line_number(result.get('element', ''))
        mapped_results.append(result)

    return mapped_results

def display_analysis_results(self, matches):
    self.view.erase_regions('wax_linter_errors')
    regions = []
    messages = {}
    point = self.view.sel()[0].begin()
    
    for match in matches:
        line_number = match['lineNumber'] - 1
        message = match['message']
        severity = match['severity']
        
        point = self.view.text_point(line_number, 0)
        region = self.view.line(point)
        regions.append(region)

        messages[str(region)] = {
            "message": match['message'],
            "severity": match['severity']
        }

    self.view.add_regions(
        'wax_linter_errors',
        regions,
        'region.redish',
        'dot',
        sublime.DRAW_OUTLINED
    )

    self.view.settings().set('wax_linter_messages', messages)


class WaxLinterEventListener(sublime_plugin.EventListener):

    def on_selection_modified_async(self, view):
        # Get stored messages from the settings
        messages = view.settings().get('wax_linter_messages', {})
        
        # Check all regions to find which one contains the cursor
        error_regions = view.get_regions('wax_linter_errors')
        for region in error_regions:
            if region.contains(view.sel()[0].begin()):
                # Use the region to lookup the stored message
                message_info = messages.get(str(region))
                if message_info:
                    # Construct the message for the tooltip
                    tooltip_content = f"<strong>WAX Linter({message_info['severity']})</strong>: {message_info['message']}"
                    # Show the tooltip at the start of the region
                    view.set_status('wax_linter_message', f"WAX Linter({message_info['severity']}): {message_info['message']}")
                    view.show_popup(tooltip_content, location=region.begin(), max_width=500)
                    break
        else:
            # Optionally clear any persistent status messages when moving away from an error region
            view.erase_status('wax_linter_message')

    def on_load_async(self, view):
        view.run_command("wax_linter")
    
    def on_pre_close(self, view):
        view.run_command("wax_linter")
    
    
    def on_post_save_async(self, view):
        view.run_command("wax_linter")
