``xpicaro`` is based on [Picaro](https://github.com/mjpost/picaro.git) (by Jason Riesa)

I've removed some functionalities and added others.

* to be used exclusively with already symmetrized alignments
* it will show alignment points using ``*``
* minimal phrases are shown with a change in background color
* unaligned words are shown in red


Aligned sentence pairs are displayed one by one by default, but ``--navigation`` offers more navigation options.


Example:

    
        python xpicaro.py example.zh-en.gdfa


# Minimal phrases

Example:

        python list_minimal_biphrases.py < example.zh-en.gdfa > example.zh-en.minphrases 
