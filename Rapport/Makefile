# Makefile for Vampires vs Werewolves AI Report
# =============================================

# Main document
MAIN = report

# LaTeX compiler
LATEX = pdflatex
LATEX_FLAGS = -interaction=nonstopmode -halt-on-error

# Default target
all: $(MAIN).pdf

# Build PDF (run twice for references)
$(MAIN).pdf: $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

# Quick build (single pass)
quick: $(MAIN).tex
	$(LATEX) $(LATEX_FLAGS) $(MAIN).tex

# Clean auxiliary files
clean:
	rm -f *.aux *.log *.out *.toc *.lof *.lot *.fls *.fdb_latexmk *.synctex.gz

# Clean everything including PDF
cleanall: clean
	rm -f $(MAIN).pdf

# Watch for changes and rebuild (requires inotify-tools)
watch:
	@echo "Watching for changes..."
	@while true; do \
		inotifywait -e modify $(MAIN).tex 2>/dev/null; \
		make quick; \
	done

# Help
help:
	@echo "Available targets:"
	@echo "  all      - Build the PDF (default)"
	@echo "  quick    - Build PDF with single LaTeX pass"
	@echo "  clean    - Remove auxiliary files"
	@echo "  cleanall - Remove all generated files"
	@echo "  watch    - Watch for changes and rebuild"
	@echo "  help     - Show this help message"

.PHONY: all quick clean cleanall watch help
