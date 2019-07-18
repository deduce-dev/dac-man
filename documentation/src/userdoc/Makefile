PS2PDF:=ps2pdf
PS2PDFOPTS:=-dSAFER -dNOPLATFONTS -dNOPAUSE -dBATCH -sPAPERSIZE=letter -dPDFSETTINGS=/prepress -dMaxSubsetPct=0 -dEmbedAllFonts=true
NAME=UserGuide
FINALNAME:=$(NAME)
GRAPHS=$(wildcard figs/*.pdf figs/results/*.pdf figs/results/depth_graphs figs/results/width_graphs figs/results/size_graphs)
FILES=$(wildcard *.tex)
REFS=$(wildcard *.bib)

all: $(FINALNAME).pdf ${NAME}.pdf

#${NAME}.pdf: ${NAME}.tex ${GRAPHS} ${FILES} ${REFS}
${NAME}.pdf: ${NAME}.tex ${FILES}
	pdflatex ${NAME}
	pdflatex ${NAME}
	pdflatex ${NAME}

%-cameraready.pdf: %.ps
	$(PS2PDF) $(PS2PDFOPTS) $< $@

clean:
	rm -f ${NAME}.pdf ${FINALNAME}.pdf ${NAME}.dvi ${NAME1}.dvi *.bbl *.aux \
	*.log *.blg *.ascii *.out *~
