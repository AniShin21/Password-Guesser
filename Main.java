import javafx.animation.TranslateTransition;
import javafx.application.Application;
import javafx.beans.property.BooleanProperty;
import javafx.beans.property.SimpleBooleanProperty;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.stage.FileChooser;
import javafx.stage.Stage;
import javafx.util.Duration;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public class PasswordApp extends Application {

    private List<String> passwords = new ArrayList<>();
    private List<String> invalidPasswords = new ArrayList<>();
    private int currentIndex = 0;
    private boolean running = false;
    private boolean keyboardAvailable = true; // Simulated keyboard presence
    private Stage primaryStage;
    private Pane root;
    private Button startButton, stopButton, statsButton, binButton, getButton;
    private Label statusLabel;
    private FileChooser fileChooser;
    private DraggableButton hoveringBtn;
    private BooleanProperty isHoveringButtonVisible = new SimpleBooleanProperty(false);
    private HBox floatingMenu; // Floating menu that contains Start, Stop, Stats buttons
    private ScheduledExecutorService executorService = Executors.newSingleThreadScheduledExecutor();
    private int passwordTypingSpeed = 1; // Passwords per second (max 5)

    public static void main(String[] args) {
        launch(args);
    }

    @Override
    public void start(Stage primaryStage) {
        this.primaryStage = primaryStage;
        root = new Pane();

        // File Chooser Setup
        fileChooser = new FileChooser();
        fileChooser.getExtensionFilters().add(new FileChooser.ExtensionFilter("Text Files", "*.txt"));

        // Create UI Components
        createUI();

        // Setup Scene
        Scene scene = new Scene(root, 600, 400);
        primaryStage.setTitle("Password Testing App");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    private void createUI() {
        // Main buttons
        getButton = createButton("Get Button", 20, 20, 150, 50);
        getButton.setOnAction(event -> showHoveringButton());

        binButton = createButton("Bin", 20, 80, 150, 50);
        binButton.setOnAction(event -> viewBin());

        startButton = createButton("Start", 20, 140, 150, 50);
        startButton.setOnAction(event -> startTyping());

        stopButton = createButton("Stop", 20, 200, 150, 50);
        stopButton.setOnAction(event -> stopTyping());

        statsButton = createButton("Stats", 20, 260, 150, 50);
        statsButton.setOnAction(event -> showStats());

        statusLabel = new Label("Keyboard Status: Hidden");
        statusLabel.setStyle("-fx-background-color: #cccccc; -fx-padding: 10;");
        statusLabel.setLayoutX(200);
        statusLabel.setLayoutY(20);

        root.getChildren().addAll(getButton, binButton, startButton, stopButton, statsButton, statusLabel);

        // Hovering Button Setup
        hoveringBtn = new DraggableButton("Start");
        hoveringBtn.setLayoutX(500);
        hoveringBtn.setLayoutY(300);
        hoveringBtn.setVisible(false);
        hoveringBtn.setOnAction(event -> toggleTestOptions());

        root.getChildren().add(hoveringBtn);

        // Floating Menu (Initially hidden)
        floatingMenu = createFloatingMenu();
        floatingMenu.setLayoutX(hoveringBtn.getLayoutX());
        floatingMenu.setLayoutY(hoveringBtn.getLayoutY() + 90);
        floatingMenu.setVisible(false);

        root.getChildren().add(floatingMenu);

        // Button Hovering Animation
        isHoveringButtonVisible.addListener((obs, oldVal, newVal) -> {
            if (newVal) {
                showHoveringButton();
            } else {
                hideHoveringButton();
            }
        });
    }

    private Button createButton(String text, double x, double y, double width, double height) {
        Button button = new Button(text);
        button.setLayoutX(x);
        button.setLayoutY(y);
        button.setMinWidth(width);
        button.setMinHeight(height);
        return button;
    }

    private HBox createFloatingMenu() {
        HBox menu = new HBox(10); // Spacing between buttons
        menu.setAlignment(Pos.CENTER);
        menu.setStyle("-fx-background-color: lightgray; -fx-padding: 10; -fx-background-radius: 5;");

        Button startButtonMenu = new Button("Start");
        startButtonMenu.setOnAction(event -> startTyping());
        Button stopButtonMenu = new Button("Stop");
        stopButtonMenu.setOnAction(event -> stopTyping());
        Button statsButtonMenu = new Button("Stats");
        statsButtonMenu.setOnAction(event -> showStats());

        menu.getChildren().addAll(startButtonMenu, stopButtonMenu, statsButtonMenu);

        return menu;
    }

    private void showHoveringButton() {
        hoveringBtn.setVisible(true);
        applyHoveringAnimation(hoveringBtn);
    }

    private void hideHoveringButton() {
        hoveringBtn.setVisible(false);
    }

    private void toggleTestOptions() {
        if (floatingMenu.isVisible()) {
            floatingMenu.setVisible(false);  // Hide options if already visible
        } else {
            // Position the floating menu near the hovering button
            floatingMenu.setLayoutX(hoveringBtn.getLayoutX());
            floatingMenu.setLayoutY(hoveringBtn.getLayoutY() + 90);
            floatingMenu.setVisible(true);  // Show options
        }
    }

    private void applyHoveringAnimation(DraggableButton button) {
        TranslateTransition transition = new TranslateTransition(Duration.seconds(0.5), button);
        transition.setByX(50); // Move the button slightly
        transition.setCycleCount(TranslateTransition.INDEFINITE);
        transition.setAutoReverse(true);
        transition.play();
    }

    private void startTyping() {
        // This method will handle the start of the password testing process
        if (passwords.isEmpty()) {
            showAlert("Error", "No passwords loaded. Please load a valid password file.");
            return;
        }

        if (running) {
            showAlert("Info", "Already running.");
            return;
        }

        running = true;
        statusLabel.setText("Testing passwords...");

        // Start typing passwords at a rate defined by passwordTypingSpeed
        executorService.scheduleAtFixedRate(this::typeNextPassword, 0, 1000 / passwordTypingSpeed, TimeUnit.MILLISECONDS);
    }

    private void stopTyping() {
        running = false;
        statusLabel.setText("Testing stopped.");
    }

    private void typeNextPassword() {
        if (!running || currentIndex >= passwords.size()) {
            return;
        }

        String password = passwords.get(currentIndex++);
        // Simulate typing password here...

        // Check keyboard status, stop if unavailable
        if (!keyboardAvailable) {
            stopTyping();
            showAlert("Info", "Keyboard disappeared. Stopping testing.");
            return;
        }

        // Add to bin if password fails (for simplicity, we'll assume all passwords are invalid)
        invalidPasswords.add(password);

        if (currentIndex >= passwords.size()) {
            showAlert("Info", "All passwords tested.");
            stopTyping();
        }
    }

    private void showStats() {
        String stats = "Tested " + currentIndex + " passwords. Invalid: " + invalidPasswords.size();
        showAlert("Stats", stats);
    }

    private void viewBin() {
        StringBuilder binContent = new StringBuilder();
        for (String password : invalidPasswords) {
            binContent.append(password).append("\n");
        }
        showAlert("Invalid Passwords", binContent.toString());
    }

    private void showAlert(String title, String message) {
        Alert alert = new Alert(Alert.AlertType.INFORMATION);
        alert.setTitle(title);
        alert.setContentText(message);
        alert.showAndWait();
    }

    // Simulating a keyboard availability check (you might implement this more fully based on actual APIs)
    private void checkKeyboardAvailability() {
        // Simulated logic to check if keyboard is available
        keyboardAvailable = true; // Set true/false based on actual condition
    }
}
