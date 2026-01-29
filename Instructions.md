Please create a static website for the life work of the photagrapher Ina Berneis. An overview of her can be found in the document "Lebenslauf.md"

The website should be bilingual, similar to the site created in "../bennoberneis/"

The style should be professional and monochromatic as most of the imagery on the site will be black and white Photographs

When styling the page implement also darkmode following the systems setting.

Please use tailwindcss for all styling and provide instructions on how to create the statis css files

Navigation bar should be vertically on the left with the following pages:

* Life
* Career
* Photography
    * Movie 1
    * Movie 2
    * ...
    * Actor 1
    * Actor 2
    * ...

The pages under "Photography" will contain text and one or more photographs.

The content for those pages can be defined in a JSON file for pre-processing.
Use the following json structure:
```
{
    title_en
    title_de
    description_en
    description_de
    [
        {
            photo1
            photo1_description_en (optional)
            photo1_description_de (optional)
        },
        {
            photo2
            photo2_description_en (optional)
            photo2_description_de (optional)
        },
        ...
    ]
}
```
"Life" and "Career" will be a micture of text and embedded Photos.

"Life" will be a historical timeline so the layout should reflect this (years only)
```
    title_en
    title_de
    description_en
    description_de
     [
        {
            date1
            description_en (optional)
            description_de (optional)
            photo1 (optional)
        },
        {
            date2
            description_en (optional)
            description_de (optional)
            photo2 (optional)
        },
        ...
    ]
}
```

The "Career" page can have just 2 sections for 'en' and 'de' and javascript to switch what is visible. - You can use the "Lebenslauf.md" page to fill in basic content (without the actor and film lists) - Add a german version by translating what you filled in for the english version

Please use only javascript for the final site to function (python can be used to generate the pages from the JSON files)

Please use dummy pictures and dummy texts so I can visualize the layout.
(same dummy picture can be used throughout the site)





    



