
latex="""
\documentclass{article}

    \usepackage{listings}
    \usepackage{color}
    
    \renewcommand\lstlistingname{Quelltext} % Change language of section name
    
    \lstset{ % General setup for the package
        language=Python,
        basicstyle=\small\sffamily,
        numbers=left,
         numberstyle=\tiny,
        frame=tb,
        tabsize=2,
        columns=fixed,
        showstringspaces=true,
        showtabs=true,
        keepspaces,
        commentstyle=\color{red},
        keywordstyle=\color{blue}
    }
    
    \begin{document}
    \begin{lstlisting}
    import os
    import subprocess
    import errno
    from .base_classes import Environment, Command, Container, LatexObject, \
        UnsafeCommand
    from .package import Package
    from .errors import CompilerError
    from .utils import dumps_list, rm_temp_dir, NoEscape
    import pylatex.config as cf
    \end{lstlisting}
    \end{document}
"""
