import markdown
import base64
import os
from glob import glob
import re
import sys
import argparse
from urllib.parse import unquote

def organise_wiki(structure, pos, to_convert, level=0):
    '''
    recurse through the wiki structure
    '''
    to_convert += [(pos + '.md', level)]

    substruct = structure.get(pos,None)
    if substruct is None:
        return to_convert
    
    else:
        for page in substruct:
            to_convert = organise_wiki(structure, os.path.join(pos,page), to_convert, level+1)
    
    return to_convert

def main(arguments):


    parser = argparse.ArgumentParser()
    parser.add_argument('wiki', help="Directory of the wiki to compile")
    parser.add_argument('--output', help="Output filename", default='export.html')
    parser.add_argument('--file_headers', help="Include headers for each file and demote subheadings", default=True)

    args = parser.parse_args(arguments)
    wiki = args.wiki

    # Read the .order files from the wiki
    structure = {}
    for order_file in glob(os.path.join(wiki,"**",".order"), recursive=True):
        structure[order_file.replace('/.order','').replace('\.order','')] = open(order_file,'r').read().split('\n')

    # organise overall document ordering
    to_convert = organise_wiki(structure, wiki,[])
    markdown_files = [(f,l) for (f,l) in to_convert if os.path.exists(f)]

    compiled = ''
    for f,l in markdown_files:

        #read the raw markdown
        doc_text = open(f,'r', encoding='utf-8').read()

        # Add title for the page name 
        if args.file_headers:
            compiled += '\n' + '#'*l + os.path.basename(f).replace('.md','') + '\n' # add filename as header
            compiled += re.sub(r'(#+)', r'\1'+'#'*l, doc_text) # demote other headers
        else:
            compiled += doc_text

    # convert to HTML
    compiled = f"# {wiki}\n" + "[TOC]\n" + compiled # put title and TOC in for whole doc
    compiled = compiled.replace('[[_TOC_]]','') # remove intermediate TOCs

    # changes headings like ##heading to ## heading
    compiled = re.sub(r'(\n#+)([^ #])(.*)', r'\1 \2\3', compiled)

    html = markdown.markdown(compiled,extensions=['tables', 'toc', 'fenced_code', 'def_list', 'nl2br', 'wikilinks','codehilite'])
    all_image_tags = re.findall(r'<img .*?>', html)
    attachments_to_encode = re.findall(r'src="([a-zA-Z0-9\/\.\-= _%\(\)]+)"', html)

    print(f'{len(attachments_to_encode)}/{len(all_image_tags)} image tags found for encoding')

    # fix image attachments
    for match in attachments_to_encode:

        clean_match = re.sub(' =[0-9]+x','',match).strip()
        clean_match = unquote(clean_match)

        extn = os.path.splitext(clean_match)[-1][1:]
        with open(wiki+clean_match,'rb') as attachment:
            b64 = base64.b64encode(attachment.read())
        html = html.replace(match, f'data:image/{extn};base64,' + b64.decode('utf-8'))

    # final HTML tidying
    html = unquote(html)

    # export the document
    with open('template.html', 'r') as template:
        template = template.read()
        html = template.replace('BODYGOESHERE',html)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Success: exported to {args.output}')

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))











